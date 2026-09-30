"""
[Q1: API Development & Error Handling]
Centralized RFC 7807 Exception Handlers
---------------------------------------
Transforms all system exceptions (Pydantic validation, HTTP errors, DB violations,
unhandled crashes) into compliant RFC 7807 Problem Details with Content-Type: application/problem+json.
Prevents stack trace leakage while providing structured debugging metadata.
"""

import logging
import traceback
from datetime import datetime, timezone
from typing import Any, List
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.schemas.problem_detail import ProblemDetail, InvalidParameter
from app.config import settings

logger = logging.getLogger("evidya.errors")


class APIProblemException(Exception):
    """
    Application-specific base exception directly convertible to RFC 7807 problem detail.
    """
    def __init__(
        self,
        status_code: int,
        title: str,
        detail: str,
        problem_type: str = "https://evidya.gujarat.gov.in/errors/general-error",
        invalid_params: List[InvalidParameter] = None,
        extra_context: dict = None
    ):
        super().__init__(detail)
        self.status_code = status_code
        self.title = title
        self.detail = detail
        self.problem_type = problem_type
        self.invalid_params = invalid_params
        self.extra_context = extra_context


def create_problem_response(
    status_code: int,
    problem_type: str,
    title: str,
    detail: str,
    instance: str,
    invalid_params: List[InvalidParameter] = None,
    extra_context: dict = None
) -> JSONResponse:
    """Helper to assemble and return application/problem+json response."""
    payload = ProblemDetail(
        type=problem_type,
        title=title,
        status=status_code,
        detail=detail,
        instance=instance,
        timestamp=datetime.now(timezone.utc).isoformat(),
        invalid_params=invalid_params,
        extra_context=extra_context if settings.DEBUG else None
    )
    return JSONResponse(
        status_code=status_code,
        content=payload.model_dump(exclude_none=True),
        headers={"Content-Type": "application/problem+json"}
    )


def register_exception_handlers(app: FastAPI) -> None:
    """
    Registers all centralized exception handlers to the FastAPI app instance.
    """

    # 1. Handle Pydantic Validation Errors (Status 422)
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        invalid_params: List[InvalidParameter] = []
        for error in exc.errors():
            loc = " -> ".join(str(l) for l in error.get("loc", []) if l != "body")
            msg = error.get("msg", "Invalid parameter")
            invalid_params.append(InvalidParameter(name=loc or "body", reason=msg))

        logger.warning(f"Validation failure on {request.url.path}: {invalid_params}")

        return create_problem_response(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            problem_type="https://evidya.gujarat.gov.in/errors/validation-error",
            title="Request Validation Failed",
            detail="One or more submitted fields violated Gujarat e-Vidya validation constraints.",
            instance=request.url.path,
            invalid_params=invalid_params
        )

    # 2. Handle Custom Domain Problem Exceptions
    @app.exception_handler(APIProblemException)
    async def domain_problem_handler(request: Request, exc: APIProblemException):
        logger.info(f"Domain problem {exc.status_code} on {request.url.path}: {exc.detail}")
        return create_problem_response(
            status_code=exc.status_code,
            problem_type=exc.problem_type,
            title=exc.title,
            detail=exc.detail,
            instance=request.url.path,
            invalid_params=exc.invalid_params,
            extra_context=exc.extra_context
        )

    # 3. Handle Standard HTTP Exceptions (400, 401, 403, 404, 409, etc.)
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        title_map = {
            400: "Bad Request",
            401: "Unauthorized Authentication Required",
            403: "Forbidden Access Denied",
            404: "Requested Resource Not Found",
            409: "Conflict / Idempotency Collision",
            429: "Too Many Requests Rate Limit Exceeded"
        }
        title = title_map.get(exc.status_code, "HTTP Error")
        problem_type = f"https://evidya.gujarat.gov.in/errors/http-{exc.status_code}"

        return create_problem_response(
            status_code=exc.status_code,
            problem_type=problem_type,
            title=title,
            detail=str(exc.detail),
            instance=request.url.path
        )

    # 4. Handle Database Integrity Errors (e.g. Unique Constraint Violations) (Status 409 / 400)
    @app.exception_handler(IntegrityError)
    async def db_integrity_handler(request: Request, exc: IntegrityError):
        logger.error(f"Database integrity conflict on {request.url.path}: {str(exc.orig)}")
        error_msg = "Database unique constraint or foreign key violation occurred."
        if "unique constraint" in str(exc.orig).lower() or "unique" in str(exc.orig).lower():
            error_msg = "A record with this identifier (e.g. Aadhaar hash or Idempotency key) already exists."

        return create_problem_response(
            status_code=status.HTTP_409_CONFLICT,
            problem_type="https://evidya.gujarat.gov.in/errors/database-conflict",
            title="Database State Conflict",
            detail=error_msg,
            instance=request.url.path
        )

    # 5. Handle Global Unhandled Exceptions (Status 500)
    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        logger.critical(f"Unhandled 500 error on {request.url.path}: {str(exc)}\n{traceback.format_exc()}")
        return create_problem_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            problem_type="https://evidya.gujarat.gov.in/errors/internal-server-error",
            title="Internal Server Error",
            detail="An unexpected internal fault occurred. The incident has been recorded for technical inspection.",
            instance=request.url.path,
            extra_context={"debug_message": str(exc)} if settings.DEBUG else None
        )
