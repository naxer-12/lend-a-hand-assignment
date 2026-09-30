"""
v1 Router Aggregator
--------------------
Bundles all feature routers under the `/api/v1` namespace.
"""

from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.api.v1.students import router as students_router
from app.api.v1.disbursements import router as disbursements_router
from app.api.v1.schools import router as schools_router
from app.api.v1.eligibility import router as eligibility_router
from app.api.v1.udise import router as udise_router
from app.api.v1.documents import router as documents_router
from app.api.v1.audit import router as audit_router

api_v1_router = APIRouter(prefix="/api/v1")

api_v1_router.include_router(auth_router)
api_v1_router.include_router(students_router)
api_v1_router.include_router(disbursements_router)
api_v1_router.include_router(schools_router)
api_v1_router.include_router(eligibility_router)
api_v1_router.include_router(udise_router)
api_v1_router.include_router(documents_router)
api_v1_router.include_router(audit_router)
