"""
[Q12: AWS S3 Storage & Security]
Document Storage & Pre-Signed URL Controller
--------------------------------------------
Implements cloud storage security requirements:
- S3 Block Public Access enforcement to safeguard student income/caste certificates.
- Generation of short-lived (5-minute / 300-second) pre-signed PUT URLs for browser-to-S3 uploads.
- Generation of short-lived (5-minute) pre-signed GET URLs for authorized viewing.
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query, status, HTTPException
from pydantic import BaseModel, Field
from app.services.s3_service import s3_service
from app.api.deps import get_current_user, CurrentUser

router = APIRouter(prefix="/documents", tags=["S3 Document Storage"])


class PresignedUploadRequest(BaseModel):
    student_id: int = Field(..., gt=0, description="Student ID owning the document")
    document_type: str = Field(
        ...,
        description="Type of certificate (e.g. INCOME_CERTIFICATE, CASTE_CERTIFICATE)",
        examples=["INCOME_CERTIFICATE"]
    )
    filename: str = Field(..., description="Original name of the file to be uploaded", examples=["income_tehsildar_2026.pdf"])
    content_type: str = Field(default="application/pdf", description="MIME type (e.g. application/pdf, image/jpeg)")


@router.post(
    "/presigned-upload",
    summary="[Q12] Generate 5-Minute Pre-Signed URL for Income Certificate Upload"
)
def create_presigned_upload_url(
    req: PresignedUploadRequest,
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    [Q12: S3 Security & Upload]
    Returns a secure 5-minute Pre-Signed PUT URL.
    Enforces student ownership check (BOLA/IDOR prevention).
    """
    if current_user.role == "STUDENT" and current_user.student_id != req.student_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: You can only upload documents for your own student profile."
        )

    # Validate file extension
    valid_extensions = {".pdf", ".jpg", ".jpeg", ".png"}
    if not any(req.filename.lower().endswith(ext) for ext in valid_extensions):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file extension. Permitted extensions: {valid_extensions}"
        )

    return s3_service.generate_presigned_upload_url(
        student_id=req.student_id,
        document_type=req.document_type,
        filename=req.filename,
        content_type=req.content_type
    )


@router.get(
    "/presigned-view",
    summary="[Q12] Generate 5-Minute Pre-Signed URL for Document Viewing"
)
def create_presigned_view_url(
    object_key: str = Query(..., description="S3 Object Key of the document"),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    [Q12: S3 Security & View]
    Generates a 5-minute Pre-Signed GET URL to view sensitive certificates.
    Requires authenticated bearer token.
    """
    return s3_service.generate_presigned_view_url(object_key)


@router.get(
    "/s3-security-status",
    summary="[Q12] Inspect AWS S3 Block Public Access & Encryption Status"
)
def get_s3_security_configuration():
    """
    Returns the Block Public Access settings and SSE-S3 encryption status.
    """
    return s3_service.enforce_bucket_public_access_block()
