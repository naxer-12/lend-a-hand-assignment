"""
Gujarat e-Vidya Scholarship Portal - Application Entrypoint
-----------------------------------------------------------
Technical Assessment Reference Implementation covering Q1 through Q12.
Production-ready FastAPI application with RFC 7807 problem details,
OWASP IDOR defense, atomic payment idempotency, and dynamic rule engines.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import init_db, SessionLocal
from app.models import School
from app.exceptions.handlers import register_exception_handlers
from app.api.v1.router import api_v1_router
from app.services.s3_service import s3_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle event managing database initialization and initial seed data."""
    init_db()

    # Apply S3 security configuration on bootstrap [Q12]
    s3_service.enforce_bucket_public_access_block()

    # Seed initial test schools if empty
    db = SessionLocal()
    try:
        count = db.query(School).count()
        if count == 0:
            sample_schools = [
                School(school_name="Shree Vidyanagar High School", district="Ahmedabad", total_students=1450, udise_code="24070100101"),
                School(school_name="Government Model Higher Secondary School", district="Gandhinagar", total_students=2100, udise_code="24060100202"),
                School(school_name="Sheth C. N. Vidyalaya", district="Ahmedabad", total_students=3200, udise_code="24070100303"),
                School(school_name="Sir J. J. English High School", district="Surat", total_students=2850, udise_code="24190100404"),
                School(school_name="Maharani Chimnabai High School", district="Vadodara", total_students=1980, udise_code="24190200505"),
                School(school_name="Saurashtra High School", district="Rajkot", total_students=1750, udise_code="24090100606"),
                School(school_name="Bhavnagar Alfred High School", district="Bhavnagar", total_students=1200, udise_code="24140100707"),
            ]
            db.add_all(sample_schools)
            db.commit()
    finally:
        db.close()

    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="State Education Portal REST API with High-Scale Resilience, OWASP IDOR defense, and RFC 7807 Error Handling.",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware for Next.js frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permits localhost:3000, 3001, etc.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Idempotent-Replay", "Content-Type"]
)

# [Q1: Error Handling] Register Centralized RFC 7807 Exception Handlers
register_exception_handlers(app)

# Include v1 REST API Router
app.include_router(api_v1_router)


@app.get("/health", tags=["Health"])
def health_check():
    """Liveness probe for orchestrators."""
    return {
        "status": "HEALTHY",
        "service": settings.PROJECT_NAME,
        "environment": settings.ENVIRONMENT,
        "version": settings.VERSION
    }
