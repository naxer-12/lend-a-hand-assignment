"""
Pytest Test Fixtures & Configuration
------------------------------------
Provides isolated in-memory test database, test client, and authenticated JWT fixtures.
"""

import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

backend_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_root))

from app.database import Base, get_db
from app.main import app
from app.models import School, Student
from app.api.deps import create_access_token
from app.services.idempotency import idempotency_service

# Isolated SQLite in-memory engine with StaticPool for test concurrency
TEST_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=test_engine)
    db = TestingSessionLocal()
    # Seed standard baseline schools
    schools = [
        School(id=1, school_name="Gandhinagar Model Higher Secondary", district="Gandhinagar", total_students=2400, udise_code="240601001"),
        School(id=2, school_name="Ahmedabad Central Vidyalaya", district="Ahmedabad", total_students=3800, udise_code="240701002"),
        School(id=3, school_name="Surat Sarvajanik School", district="Surat", total_students=4100, udise_code="241901003"),
        School(id=4, school_name="Vadodara State High School", district="Vadodara", total_students=2900, udise_code="241902004"),
        School(id=5, school_name="Rajkot Saurashtra Vidyalaya", district="Rajkot", total_students=3500, udise_code="240901005"),
        School(id=6, school_name="Bhavnagar Alfred School", district="Bhavnagar", total_students=1800, udise_code="241401006"),
    ]
    db.add_all(schools)
    db.commit()

    # Seed baseline students
    students = [
        Student(
            id=1,
            first_name="Aarav",
            last_name="Patel",
            aadhaar_hash="1111111111111111111111111111111111111111111111111111111111111111",
            aadhaar_masked="XXXX-XXXX-1111",
            bank_account_masked="XXXXXXXX1111",
            family_income=150000.0,
            district="Gandhinagar",
            school_id=1,
            attendance_percentage=88.0,
            marks_percentage=82.0,
            category="GENERAL"
        ),
        Student(
            id=2,
            first_name="Diya",
            last_name="Shah",
            aadhaar_hash="2222222222222222222222222222222222222222222222222222222222222222",
            aadhaar_masked="XXXX-XXXX-2222",
            bank_account_masked="XXXXXXXX2222",
            family_income=220000.0,
            district="Gandhinagar",
            school_id=1,
            attendance_percentage=92.0,
            marks_percentage=89.0,
            category="GENERAL"
        ),
        Student(
            id=3,
            first_name="Rohan",
            last_name="Parmar",
            aadhaar_hash="3333333333333333333333333333333333333333333333333333333333333333",
            aadhaar_masked="XXXX-XXXX-3333",
            bank_account_masked="XXXXXXXX3333",
            family_income=90000.0,
            district="Surat",
            school_id=3,
            attendance_percentage=79.0,
            marks_percentage=68.0,
            category="SC"
        )
    ]
    db.add_all(students)
    db.commit()
    db.close()
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def db_session():
    connection = test_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def clear_idempotency_cache():
    idempotency_service.in_memory_store.clear()
    yield


# --- Authenticated Token Fixtures for Q10 IDOR / BOLA Testing ---
@pytest.fixture
def token_student_1():
    return create_access_token(user_id="student_aarav", role="STUDENT", student_id=1, district="Gandhinagar")


@pytest.fixture
def token_student_2():
    return create_access_token(user_id="student_diya", role="STUDENT", student_id=2, district="Gandhinagar")


@pytest.fixture
def token_officer_gandhinagar():
    return create_access_token(user_id="officer_gn", role="DISTRICT_OFFICER", district="Gandhinagar")


@pytest.fixture
def token_officer_surat():
    return create_access_token(user_id="officer_srt", role="DISTRICT_OFFICER", district="Surat")


@pytest.fixture
def token_state_admin():
    return create_access_token(user_id="admin_gujarat", role="STATE_ADMIN")
