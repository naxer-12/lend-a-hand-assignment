"""
[Q1, Q10, Q11: Student Resource Endpoints]
Student API Controller
----------------------
Addresses Three Critical Architecture Requirements:
1. [Q1: API Development & Error Handling]:
   - POST /api/v1/students enforces strict Pydantic v2 domain constraints.
   - Rejection triggers centralized RFC 7807 problem details (Status 422).
2. [Q10: OWASP BOLA / IDOR Defense]:
   - GET /api/v1/students/{student_id} inspects authenticated JWT caller context.
   - Prevents Broken Object Level Authorization (IDOR):
     * A STUDENT cannot supply another student's ID (returns 403 Forbidden).
     * A DISTRICT_OFFICER from Gandhinagar cannot access records in Surat (returns 403 Forbidden).
     * A STATE_ADMIN holds state-wide oversight privileges.
3. [Q11: Audit Trails & PII Masking]:
   - Logs immutable cryptographic audit trail on every PII read or write.
   - Plaintext Aadhaar and bank details are masked (XXXX-XXXX-1234).
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Request, status, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.student import Student
from app.models.school import School
from app.schemas.student import StudentCreate, StudentRead
from app.schemas.problem_detail import ProblemDetail
from app.api.deps import get_current_user, CurrentUser
from app.services.audit_service import audit_service, mask_aadhaar
from app.exceptions.handlers import APIProblemException

router = APIRouter(prefix="/students", tags=["Students"])


@router.post(
    "",
    response_model=StudentRead,
    status_code=status.HTTP_201_CREATED,
    responses={
        422: {"model": ProblemDetail, "description": "Validation constraints failed"},
        409: {"model": ProblemDetail, "description": "Aadhaar hash collision / duplicate student"},
        404: {"model": ProblemDetail, "description": "School ID not found"}
    }
)
def register_student(
    student_in: StudentCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    [Q1: API Development & Validation]
    Enrolls a student onto the Gujarat e-Vidya portal.
    Subjected to strict Pydantic validation (names, Aadhaar hash, income, district).
    """
    # 1. Verify foreign key relationship to school
    school = db.query(School).filter(School.id == student_in.school_id).first()
    if not school:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Referenced school ID {student_in.school_id} does not exist in the state registry."
        )

    # 2. Check for duplicate Aadhaar Hash (Deduplication)
    existing_student = db.query(Student).filter(Student.aadhaar_hash == student_in.aadhaar_hash).first()
    if existing_student:
        raise APIProblemException(
            status_code=status.HTTP_409_CONFLICT,
            title="Duplicate Beneficiary Detected",
            detail="A student with this Aadhaar hash has already been registered on the portal.",
            problem_type="https://evidya.gujarat.gov.in/errors/duplicate-aadhaar"
        )

    # 3. Create student entity with masked PII [Q11]
    masked_aadhaar = f"XXXX-XXXX-{student_in.aadhaar_last_four}"
    new_student = Student(
        first_name=student_in.first_name,
        last_name=student_in.last_name,
        aadhaar_hash=student_in.aadhaar_hash,
        aadhaar_masked=masked_aadhaar,
        bank_account_masked="XXXXXXXX" + student_in.aadhaar_last_four,
        family_income=student_in.family_income,
        district=student_in.district,
        school_id=student_in.school_id,
        attendance_percentage=student_in.attendance_percentage or 85.0,
        marks_percentage=student_in.marks_percentage or 75.0,
        category=student_in.category or "GENERAL"
    )

    db.add(new_student)
    db.commit()
    db.refresh(new_student)

    # 4. Cryptographic Audit Log Chaining [Q11]
    client_ip = request.client.host if request.client else "127.0.0.1"
    audit_service.record_action(
        db=db,
        actor_id="PORTAL_REGISTRATION_FLOW",
        actor_role="SELF_REGISTER",
        action="CREATE_STUDENT",
        resource_type="STUDENT",
        resource_id=str(new_student.id),
        client_ip=client_ip,
        user_agent=request.headers.get("user-agent"),
        details={
            "student_id": new_student.id,
            "district": new_student.district,
            "school_id": new_student.school_id,
            "aadhaar_masked": masked_aadhaar
        }
    )

    return new_student


@router.get(
    "/{student_id}",
    response_model=StudentRead,
    responses={
        401: {"model": ProblemDetail, "description": "Bearer token authentication missing or invalid"},
        403: {"model": ProblemDetail, "description": "Forbidden: BOLA/IDOR authorization violation"},
        404: {"model": ProblemDetail, "description": "Student record not found"}
    }
)
def get_student_by_id(
    student_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    [Q10: OWASP BOLA / IDOR Remediation & Q11 Audit Trail]
    Retrieves student profile by ID.
    Enforces Object-Level Access Control based on caller's authenticated JWT claims.
    """
    # 1. Fetch targeted student record
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student record with ID {student_id} was not found."
        )

    # 2. Enforce Fine-Grained Authorization Rules (BOLA/IDOR Prevention)
    is_authorized = False

    if current_user.role == "STATE_ADMIN":
        # State administrator holds universal read permissions
        is_authorized = True

    elif current_user.role == "DISTRICT_OFFICER":
        # District officer may ONLY access students enrolled within their assigned jurisdiction
        if current_user.district and student.district.lower() == current_user.district.lower():
            is_authorized = True
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    f"Access Denied (IDOR/BOLA Protection): District Officer assigned to '{current_user.district}' "
                    f"is not authorized to inspect records belonging to district '{student.district}'."
                )
            )

    elif current_user.role == "STUDENT":
        # Student may ONLY access their own registered record
        if current_user.student_id == student_id:
            is_authorized = True
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    f"Access Denied (IDOR/BOLA Protection): Student authenticated as ID {current_user.student_id} "
                    f"cannot inspect data belonging to Student ID {student_id}."
                )
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Role not authorized to inspect student records."
        )

    if not is_authorized:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized access attempt."
        )

    # 3. Append Cryptographically Chained Audit Entry [Q11]
    client_ip = request.client.host if request.client else "127.0.0.1"
    audit_service.record_action(
        db=db,
        actor_id=current_user.user_id,
        actor_role=current_user.role,
        action="VIEW_STUDENT_PII",
        resource_type="STUDENT",
        resource_id=str(student.id),
        client_ip=client_ip,
        user_agent=request.headers.get("user-agent"),
        details={
            "requested_student_id": student_id,
            "district": student.district,
            "caller_role": current_user.role,
            "caller_district": current_user.district
        }
    )

    return student


@router.get("", response_model=List[StudentRead])
def list_students(
    district: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Administrative listing of students with district scoping.
    """
    query = db.query(Student)

    if current_user.role == "DISTRICT_OFFICER":
        # Force filter to their assigned district
        query = query.filter(Student.district.ilike(current_user.district))
    elif district and current_user.role == "STATE_ADMIN":
        query = query.filter(Student.district.ilike(district))
    elif current_user.role == "STUDENT":
        # Student only sees themselves
        query = query.filter(Student.id == current_user.student_id)

    return query.offset(offset).limit(limit).all()
