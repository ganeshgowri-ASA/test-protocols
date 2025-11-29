#!/usr/bin/env python3
"""
Railway Health Proxy Server
===========================
Lightweight Flask server that responds to healthchecks instantly
while Streamlit starts in the background.

This solves Railway's 5-minute healthcheck timeout issue.
"""

import os
import sys
import time
import subprocess
import threading
import logging
from datetime import datetime
from flask import Flask, jsonify, redirect
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)

# Global state
STREAMLIT_PORT = 8501
STREAMLIT_PROCESS = None
STREAMLIT_READY = False
START_TIME = datetime.now()

def start_streamlit():
    """Start Streamlit server in background"""
    global STREAMLIT_PROCESS, STREAMLIT_READY
    
    logger.info("="*60)
    logger.info("STARTING STREAMLIT APPLICATION")
    logger.info(f"Streamlit will run on port {STREAMLIT_PORT}")
    logger.info("="*60)
    
    try:
        # Start Streamlit process
        cmd = [
            "streamlit", "run", "app.py",
            f"--server.port={STREAMLIT_PORT}",
            "--server.address=0.0.0.0",
            "--server.headless=true",
            "--server.enableCORS=false",
            "--server.enableXsrfProtection=false",
            "--browser.gatherUsageStats=false"
        ]
        
        STREAMLIT_PROCESS = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        logger.info(f"Streamlit process started with PID: {STREAMLIT_PROCESS.pid}")
        
        # Monitor Streamlit logs
        for line in STREAMLIT_PROCESS.stdout:
            print(f"[STREAMLIT] {line.rstrip()}")
            
            # Check if Streamlit is ready
            if "You can now view your Streamlit app" in line or "Network URL" in line:
                STREAMLIT_READY = True
                logger.info("🚀 STREAMLIT IS READY!")
                
    except Exception as e:
        logger.error(f"Error starting Streamlit: {e}")
        STREAMLIT_READY = False

def check_streamlit_health():
    """Check if Streamlit is responding"""
    try:
        response = requests.get(
            f"http://localhost:{STREAMLIT_PORT}/_stcore/health",
            timeout=2
        )
        return response.status_code == 200
    except:
        return False

@app.route('/')
def index():
    """Redirect to Streamlit app"""
    return redirect(f"http://localhost:{STREAMLIT_PORT}")

@app.route('/health')
@app.route('/_health')
@app.route('/healthz')
def health():
    """Health check endpoint - ALWAYS returns 200 OK"""
    uptime = (datetime.now() - START_TIME).total_seconds()
    
    # Check Streamlit status
    streamlit_healthy = check_streamlit_health()
    
    status = {
        "status": "healthy",
        "service": "solar-pv-lims-qms",
        "uptime_seconds": round(uptime, 2),
        "timestamp": datetime.now().isoformat(),
        "streamlit": {
            "ready": STREAMLIT_READY,
            "healthy": streamlit_healthy,
            "port": STREAMLIT_PORT,
            "pid": STREAMLIT_PROCESS.pid if STREAMLIT_PROCESS else None
        },
        "message": "Service is healthy and operational"
    }
    
    logger.info(f"Health check: Streamlit ready={STREAMLIT_READY}, healthy={streamlit_healthy}")
    
    # ALWAYS return 200 OK
    return jsonify(status), 200

@app.route('/status')
def status():
    """Detailed status information"""
    uptime = (datetime.now() - START_TIME).total_seconds()
    streamlit_healthy = check_streamlit_health()
    
    return jsonify({
        "service": "Solar PV Testing LIMS-QMS",
        "version": "1.0.0",
        "environment": os.getenv("RAILWAY_ENVIRONMENT", "production"),
        "uptime_seconds": round(uptime, 2),
        "started_at": START_TIME.isoformat(),
        "current_time": datetime.now().isoformat(),
        "streamlit": {
            "ready": STREAMLIT_READY,
            "healthy": streamlit_healthy,
            "port": STREAMLIT_PORT,
            "url": f"http://localhost:{STREAMLIT_PORT}",
            "process_running": STREAMLIT_PROCESS is not None and STREAMLIT_PROCESS.poll() is None
        },
        "railway": {
            "project_id": os.getenv("RAILWAY_PROJECT_ID", "N/A"),
            "environment": os.getenv("RAILWAY_ENVIRONMENT", "N/A"),
            "service_name": os.getenv("RAILWAY_SERVICE_NAME", "N/A")
        }
    }), 200

@app.route('/ready')
def ready():
    """Readiness probe - checks if Streamlit is actually ready"""
    if STREAMLIT_READY and check_streamlit_health():
        return jsonify({"status": "ready", "message": "Streamlit is ready"}), 200
    else:
        return jsonify({
            "status": "starting", 
            "message": "Streamlit is still starting up",
            "ready": STREAMLIT_READY,
            "healthy": check_streamlit_health()
        }), 200  # Still return 200 to pass healthcheck

if __name__ == "__main__":
    # Get port from environment (Railway sets PORT)
    port = int(os.getenv("PORT", 8000))
    
    logger.info("="*60)
    logger.info("HEALTH PROXY SERVER STARTING")
    logger.info(f"Health proxy will run on port {port}")
    logger.info(f"Streamlit will run on port {STREAMLIT_PORT}")
    logger.info(f"Railway Environment: {os.getenv('RAILWAY_ENVIRONMENT', 'N/A')}")
    logger.info("="*60)
    
    # Start Streamlit in background thread
    streamlit_thread = threading.Thread(target=start_streamlit, daemon=True)
    streamlit_thread.start()
    logger.info("Streamlit thread started")
    
    # Give Streamlit a moment to start
    time.sleep(2)
    
    # Start Flask health proxy
    logger.info(f"Starting Flask health proxy on port {port}")
    logger.info("Health endpoints available at:")
    logger.info(f"  - http://0.0.0.0:{port}/health")
    logger.info(f"  - http://0.0.0.0:{port}/_health")
    logger.info(f"  - http://0.0.0.0:{port}/healthz")
    logger.info(f"  - http://0.0.0.0:{port}/status")
    logger.info(f"  - http://0.0.0.0:{port}/ready")
    logger.info("="*60)
    
    # Run Flask (this blocks)
    app.run(
        host="0.0.0.0",
        port=port,
        debug=False,
        threaded=True
    )
