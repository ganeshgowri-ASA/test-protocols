# SQLAlchemy 2.0 Migration - Detailed Implementation Guide

## Status Summary

### Completed Fixes (Phase 1-2)
- ✅ **app.py**: Fixed initialization order - database init moved after logger creation
- ✅ **database/models.py**: Removed duplicate CompanyProfile class definition (13 lines)
- ✅ **pages/2_Service_Request.py**: Added SQLAlchemy 2.0 imports (line 21)

### Remaining Work (Phase 2D - Query Syntax Migration)

All files need replacement of `.query()` calls with `select()` syntax.

## File-by-File Migration Details

### File 1: pages/2_Service_Request.py
**Status**: Imports added, query fixes needed
**Queries to fix**: 2

**Query 1 (Line 257-259)**
```python
# BEFORE:
requests = db.query(ServiceRequest).order_by(
    ServiceRequest.created_at.desc()
).limit(50).all()

# AFTER:
requests = db.execute(
    select(ServiceRequest)
    .order_by(desc(ServiceRequest.created_at))
    .limit(50)
).scalars().all()
```

**Query 2 (Line 289-293)**
```python
# BEFORE:
results = db.query(ServiceRequest).filter(
    (ServiceRequest.request_number.contains(search_query)) |
    (ServiceRequest.client_name.contains(search_query)) |
    (ServiceRequest.client_email.contains(search_query))
).all()

# AFTER:
results = db.execute(
    select(ServiceRequest).where(
        or_(
            ServiceRequest.request_number.contains(search_query),
            ServiceRequest.client_name.contains(search_query),
            ServiceRequest.client_email.contains(search_query)
        )
    )
).scalars().all()
```

## Summary
- Total .query() patterns identified: 45+
- Estimated fixes needed: 45
- Files affected: 7
- Imports required: Already added to Service_Request.py
- Pattern complexity: Multiple (.order_by, .filter, .limit combinations)

## Implementation Notes
- Use `db.execute(select(...)).scalars()` for object queries
- Replace `.filter()` with `.where()`  
- Replace `.order_by(Model.field.desc())` with `.order_by(desc(Model.field))`
- Use `and_()` for multiple AND conditions
- Use `or_()` for multiple OR conditions
- Always end with `.all()` or `.first()` after `.scalars()`

## Next Steps
1. Apply imports to remaining 6 files
2. Systematically migrate each .query() call
3. Commit in logical batches
4. Local testing with `streamlit run app.py`
5. Deploy to Railway
