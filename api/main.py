"""
FastAPI Integration API - RESTful endpoints for workflow orchestration.

Provides programmatic access to all workflow components for integration with:
- LIMS (Laboratory Information Management Systems)
- QMS (Quality Management Systems)
- PM Systems (Project Management Systems)
- External customers and partners
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from workflow.orchestrator import WorkflowOrchestrator
from handlers.service_request_handler import ServiceRequestHandler
from handlers.incoming_inspection_handler import IncomingInspectionHandler
from handlers.equipment_scheduler import EquipmentScheduler
from workflow.protocol_dispatcher import ProtocolDispatcher
from workflow.report_aggregator import ReportAggregator
from traceability.traceability_engine import TraceabilityEngine

# Initialize FastAPI app
app = FastAPI(
    title="PV Testing Protocol Framework API",
    description="RESTful API for workflow orchestration and traceability",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize handlers (singleton pattern)
orchestrator = WorkflowOrchestrator()
service_request_handler = ServiceRequestHandler()
inspection_handler = IncomingInspectionHandler()
equipment_scheduler = EquipmentScheduler()
protocol_dispatcher = ProtocolDispatcher()
report_aggregator = ReportAggregator()
traceability_engine = TraceabilityEngine()

# Register handlers
orchestrator.register_handlers(
    service_request_handler,
    inspection_handler,
    equipment_scheduler,
    protocol_dispatcher,
    report_aggregator
)


# ============================================================================
# Pydantic Models for Request/Response
# ============================================================================

class ServiceRequestCreate(BaseModel):
    """Model for creating service request"""
    requested_by: Dict[str, Any]
    project_customer: Dict[str, Any]
    sample_details: Dict[str, Any]
    protocols_requested: List[Dict[str, str]]
    priority: str = "Normal"
    requested_completion_date: Optional[str] = None
    special_requirements: Optional[Dict[str, Any]] = None


class InspectionCreate(BaseModel):
    """Model for creating inspection"""
    service_request_id: str
    inspector_info: Dict[str, Any]


class AcceptanceDecision(BaseModel):
    """Model for inspection acceptance decision"""
    decision: str
    decision_by: str
    rationale: str
    conditions: Optional[List[str]] = None
    hold_reason: Optional[str] = None
    reject_reason: Optional[str] = None


class EquipmentPlanCreate(BaseModel):
    """Model for creating equipment plan"""
    work_order_id: str
    service_request_id: str
    protocols_to_execute: List[Dict[str, Any]]


# ============================================================================
# Health Check Endpoints
# ============================================================================

@app.get("/", tags=["Health"])
async def root():
    """Root endpoint - API health check"""
    return {
        "message": "PV Testing Protocol Framework API",
        "version": "1.0.0",
        "status": "operational",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api/health", tags=["Health"])
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "components": {
            "orchestrator": "operational",
            "service_requests": "operational",
            "inspections": "operational",
            "equipment": "operational",
            "protocols": "operational",
            "reports": "operational",
            "traceability": "operational"
        },
        "timestamp": datetime.now().isoformat()
    }


# ============================================================================
# Service Request Endpoints
# ============================================================================

@app.post("/api/service-requests", tags=["Service Requests"])
async def create_service_request(request: ServiceRequestCreate):
    """Create a new service request"""
    success, message, request_data = service_request_handler.create_service_request(
        request.dict()
    )

    if success:
        # Record traceability event
        traceability_engine.record_event(
            event_type="create",
            entity_type="service_request",
            entity_id=request_data["request_id"],
            action="Service request created via API",
            user="API User",
            data={"status": "Draft"}
        )

        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={
                "success": True,
                "message": message,
                "data": request_data
            }
        )
    else:
        raise HTTPException(status_code=400, detail=message)


@app.get("/api/service-requests", tags=["Service Requests"])
async def list_service_requests(status_filter: Optional[str] = None):
    """List all service requests with optional status filter"""
    requests = service_request_handler.list_service_requests(status_filter)
    return {
        "success": True,
        "count": len(requests),
        "data": requests
    }


@app.get("/api/service-requests/{request_id}", tags=["Service Requests"])
async def get_service_request(request_id: str):
    """Get service request by ID"""
    request_data = service_request_handler.get_service_request(request_id)

    if request_data:
        return {
            "success": True,
            "data": request_data
        }
    else:
        raise HTTPException(status_code=404, detail=f"Service request {request_id} not found")


@app.post("/api/service-requests/{request_id}/submit", tags=["Service Requests"])
async def submit_service_request(request_id: str):
    """Submit service request for approval"""
    success, message = service_request_handler.submit_service_request(request_id)

    if success:
        traceability_engine.record_event(
            event_type="submit",
            entity_type="service_request",
            entity_id=request_id,
            action="Service request submitted via API",
            user="API User"
        )

        return {"success": True, "message": message}
    else:
        raise HTTPException(status_code=400, detail=message)


@app.post("/api/service-requests/{request_id}/approve", tags=["Service Requests"])
async def approve_service_request(request_id: str, approved_by: str):
    """Approve service request"""
    success, message, work_orders = service_request_handler.approve_service_request(
        request_id, approved_by
    )

    if success:
        # Get request data and initiate workflow
        request_data = service_request_handler.get_service_request(request_id)
        workflow = orchestrator.initiate_workflow(request_data)

        traceability_engine.record_event(
            event_type="approve",
            entity_type="service_request",
            entity_id=request_id,
            action="Service request approved via API",
            user=approved_by,
            data={"work_orders": work_orders, "workflow_id": workflow["workflow_id"]}
        )

        return {
            "success": True,
            "message": message,
            "work_orders": work_orders,
            "workflow_id": workflow["workflow_id"]
        }
    else:
        raise HTTPException(status_code=400, detail=message)


# ============================================================================
# Incoming Inspection Endpoints
# ============================================================================

@app.post("/api/inspections", tags=["Inspections"])
async def create_inspection(inspection: InspectionCreate):
    """Create a new incoming inspection"""
    success, message, inspection_data = inspection_handler.create_inspection(
        inspection.service_request_id,
        inspection.inspector_info
    )

    if success:
        traceability_engine.record_event(
            event_type="create",
            entity_type="inspection",
            entity_id=inspection_data["inspection_id"],
            action="Inspection created via API",
            user=inspection.inspector_info.get("name", "API User")
        )

        # Link to service request
        traceability_engine.record_entity_link(
            "service_request", inspection.service_request_id,
            "inspection", inspection_data["inspection_id"],
            "triggers"
        )

        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={
                "success": True,
                "message": message,
                "data": inspection_data
            }
        )
    else:
        raise HTTPException(status_code=400, detail=message)


@app.get("/api/inspections", tags=["Inspections"])
async def list_inspections(status_filter: Optional[str] = None):
    """List all inspections"""
    inspections = inspection_handler.list_inspections(status_filter)
    return {
        "success": True,
        "count": len(inspections),
        "data": inspections
    }


@app.get("/api/inspections/{inspection_id}", tags=["Inspections"])
async def get_inspection(inspection_id: str):
    """Get inspection by ID"""
    inspection_data = inspection_handler.get_inspection(inspection_id)

    if inspection_data:
        return {
            "success": True,
            "data": inspection_data
        }
    else:
        raise HTTPException(status_code=404, detail=f"Inspection {inspection_id} not found")


@app.post("/api/inspections/{inspection_id}/decision", tags=["Inspections"])
async def make_acceptance_decision(inspection_id: str, decision: AcceptanceDecision):
    """Make acceptance decision for inspection"""
    success, message = inspection_handler.make_acceptance_decision(
        inspection_id,
        decision.decision,
        decision.decision_by,
        decision.rationale,
        conditions=decision.conditions,
        hold_reason=decision.hold_reason,
        reject_reason=decision.reject_reason
    )

    if success:
        traceability_engine.record_event(
            event_type="decision",
            entity_type="inspection",
            entity_id=inspection_id,
            action=f"Acceptance decision: {decision.decision}",
            user=decision.decision_by
        )

        return {"success": True, "message": message}
    else:
        raise HTTPException(status_code=400, detail=message)


# ============================================================================
# Equipment Planning Endpoints
# ============================================================================

@app.post("/api/equipment/plans", tags=["Equipment"])
async def create_equipment_plan(plan: EquipmentPlanCreate):
    """Create equipment planning"""
    success, message, plan_data = equipment_scheduler.create_equipment_plan(
        plan.work_order_id,
        plan.service_request_id,
        plan.protocols_to_execute
    )

    if success:
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={
                "success": True,
                "message": message,
                "data": plan_data
            }
        )
    else:
        raise HTTPException(status_code=400, detail=message)


@app.get("/api/equipment", tags=["Equipment"])
async def list_equipment(status_filter: Optional[str] = None):
    """List all equipment"""
    equipment = equipment_scheduler.list_equipment(status_filter)
    return {
        "success": True,
        "count": len(equipment),
        "data": equipment
    }


# ============================================================================
# Protocol Endpoints
# ============================================================================

@app.get("/api/protocols", tags=["Protocols"])
async def list_protocols(category_filter: Optional[str] = None):
    """List available protocols"""
    protocols = protocol_dispatcher.list_protocols(category_filter)
    return {
        "success": True,
        "count": len(protocols),
        "data": protocols
    }


@app.get("/api/protocols/{protocol_id}", tags=["Protocols"])
async def get_protocol_details(protocol_id: str):
    """Get protocol details"""
    protocol = protocol_dispatcher.get_protocol_details(protocol_id)

    if protocol:
        return {
            "success": True,
            "data": protocol
        }
    else:
        raise HTTPException(status_code=404, detail=f"Protocol {protocol_id} not found")


@app.get("/api/protocols/executions", tags=["Protocols"])
async def list_protocol_executions(status_filter: Optional[str] = None):
    """List protocol executions"""
    executions = protocol_dispatcher.list_executions(status_filter)
    return {
        "success": True,
        "count": len(executions),
        "data": executions
    }


# ============================================================================
# Workflow Endpoints
# ============================================================================

@app.get("/api/workflows", tags=["Workflows"])
async def list_workflows(status_filter: Optional[str] = None):
    """List all workflows"""
    workflows = orchestrator.list_active_workflows(status_filter)
    return {
        "success": True,
        "count": len(workflows),
        "data": workflows
    }


@app.get("/api/workflows/{workflow_id}", tags=["Workflows"])
async def get_workflow_status(workflow_id: str):
    """Get workflow status"""
    try:
        status_info = orchestrator.get_workflow_status(workflow_id)
        return {
            "success": True,
            "data": status_info
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ============================================================================
# Traceability Endpoints
# ============================================================================

@app.get("/api/traceability/audit-trail", tags=["Traceability"])
async def get_audit_trail(
    entity_type: Optional[str] = None,
    entity_id: Optional[str] = None,
    user: Optional[str] = None
):
    """Get audit trail with filters"""
    trail = traceability_engine.get_audit_trail(
        entity_type=entity_type,
        entity_id=entity_id,
        user=user
    )
    return {
        "success": True,
        "count": len(trail),
        "data": trail
    }


@app.get("/api/traceability/lineage/{entity_type}/{entity_id}", tags=["Traceability"])
async def get_entity_lineage(entity_type: str, entity_id: str):
    """Get complete lineage for an entity"""
    lineage = traceability_engine.get_entity_lineage(entity_type, entity_id)
    return {
        "success": True,
        "data": lineage
    }


@app.post("/api/traceability/report/{entity_type}/{entity_id}", tags=["Traceability"])
async def generate_traceability_report(entity_type: str, entity_id: str):
    """Generate comprehensive traceability report"""
    report = traceability_engine.generate_traceability_report(entity_type, entity_id)
    return {
        "success": True,
        "data": report
    }


@app.get("/api/traceability/statistics", tags=["Traceability"])
async def get_traceability_statistics():
    """Get traceability statistics"""
    stats = traceability_engine.get_statistics()
    return {
        "success": True,
        "data": stats
    }


# ============================================================================
# Reports Endpoints
# ============================================================================

@app.get("/api/reports", tags=["Reports"])
async def list_reports(status_filter: Optional[str] = None):
    """List all reports"""
    reports = report_aggregator.list_reports(status_filter)
    return {
        "success": True,
        "count": len(reports),
        "data": reports
    }


@app.get("/api/reports/{report_id}", tags=["Reports"])
async def get_report(report_id: str):
    """Get report by ID"""
    report = report_aggregator.get_report(report_id)

    if report:
        return {
            "success": True,
            "data": report
        }
    else:
        raise HTTPException(status_code=404, detail=f"Report {report_id} not found")


# Run with: uvicorn api.main:app --reload
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
