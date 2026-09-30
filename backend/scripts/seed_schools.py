"""
Database Seeder for High-Performance Dashboard Testing
-------------------------------------------------------
Generates 1,000+ realistic Gujarat schools across all 33 districts
to stress-test:
- [Q4]: Optimized raw SQL top 5 query against 1,000+ indexed rows.
- [Q3 & Q8]: Next.js 14 virtualized table rendering 1,000+ rows smoothly at 60 FPS.
"""

import sys
import random
from pathlib import Path

backend_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_root))

from app.database import SessionLocal, init_db
from app.models.school import School
from app.schemas.student import VALID_GUJARAT_DISTRICTS

SCHOOL_PREFIXES = [
    "Government Model High School",
    "Shree Sardar Vallabhbhai Patel Vidyalaya",
    "Kasturba Gandhi Balika Vidyalaya",
    "Mahatma Gandhi Memorial Secondary School",
    "Shree Swaminarayan Gurukul Vidyalaya",
    "Navchetan Sarvajanik High School",
    "Shree Vidya Mandir Higher Secondary",
    "Adarsh Kanya Shala",
    "Prathmik Shala",
    "Smt. Maniben High School",
    "Sheth M. N. Vidyalaya",
    "Vivekananda English Medium School",
    "Gujarat Secondary & Higher Secondary Vidyalaya",
    "Shree Saurashtra Rashtriya Shala"
]

AREAS = [
    "Navrangpura", "Satellite", "Maninagar", "Infocity", "Sector 7", "Sector 21",
    "Varachha", "Adajan", "Athwa Lines", "Alkapuri", "Fatehgunj", "Karelibaug",
    "Kalawad Road", "Yagnik Road", "Talaja", "Palitana", "Veraval", "Anjar",
    "Gandhidham", "Bhuj", "Visnagar", "Kadi", "Patan City", "Modasa", "Lunawada"
]


def seed_large_school_dataset(target_count: int = 1200):
    init_db()
    session = SessionLocal()

    existing_count = session.query(School).count()
    if existing_count >= target_count:
        print(f"Schools database already populated with {existing_count} records.")
        session.close()
        return

    print(f"Current count: {existing_count}. Generating {target_count - existing_count} new Gujarat school records...")

    districts = list(sorted(VALID_GUJARAT_DISTRICTS))
    schools_to_add = []

    # Inject specific high-enrollment top schools
    top_anchor_schools = [
        ("The Gujarat National Model Higher Secondary", "Gandhinagar", 4850, "24060100999"),
        ("Sardar Patel Sarvajanik Vidyalaya", "Ahmedabad", 4620, "24070100888"),
        ("Surat Diamond City Excellence High School", "Surat", 4410, "24190100777"),
        ("Maharaja Sayajirao Model Vidyalaya", "Vadodara", 4190, "24190200666"),
        ("Saurashtra State Premier High School", "Rajkot", 3950, "24090100555"),
    ]

    for name, dist, count, udise in top_anchor_schools:
        schools_to_add.append(
            School(school_name=name, district=dist, total_students=count, udise_code=udise)
        )

    # Generate remaining schools evenly across all 33 districts
    idx = 1
    while len(schools_to_add) < (target_count - existing_count):
        district = districts[idx % len(districts)]
        prefix = random.choice(SCHOOL_PREFIXES)
        area = random.choice(AREAS)
        name = f"{prefix} - {area}, {district}"
        students = random.randint(150, 3500)
        udise = f"24{random.randint(10, 33)}{random.randint(1000000, 9999999)}"

        schools_to_add.append(
            School(school_name=name, district=district, total_students=students, udise_code=udise)
        )
        idx += 1

    session.add_all(schools_to_add)
    session.commit()
    total = session.query(School).count()
    session.close()
    print(f"Successfully seeded! Total schools in database now: {total}")


if __name__ == "__main__":
    seed_large_school_dataset(1200)
