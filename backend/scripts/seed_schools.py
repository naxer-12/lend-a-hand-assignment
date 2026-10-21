"""
Database Seeder for High-Performance Dashboard & Analytics Testing
-------------------------------------------------------------------
Generates 50,000+ realistic Gujarat schools across all 33 districts
to stress-test:
- [Q4]: Optimized raw SQL top 5 query against 50,000+ indexed rows.
- [Q3 & Q8]: Next.js 14 virtualized table rendering 10,000+ rows smoothly at 60 FPS.
"""

import sys
import random
import argparse
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


def seed_large_school_dataset(target_count: int = 50000, batch_size: int = 5000):
    init_db()
    session = SessionLocal()

    existing_count = session.query(School).count()
    if existing_count >= target_count:
        print(f"Schools database already populated with {existing_count} records.")
        session.close()
        return

    remaining = target_count - existing_count
    print(f"Current count: {existing_count}. Generating {remaining} new Gujarat school records in batches of {batch_size}...")

    districts = list(sorted(VALID_GUJARAT_DISTRICTS))
    
    # Inject top anchor schools if count is zero
    if existing_count == 0:
        top_anchor_schools = [
            {"school_name": "The Gujarat National Model Higher Secondary", "district": "Gandhinagar", "total_students": 5200, "udise_code": "24060100999"},
            {"school_name": "Sardar Patel Sarvajanik Vidyalaya", "district": "Ahmedabad", "total_students": 4980, "udise_code": "24070100888"},
            {"school_name": "Surat Diamond City Excellence High School", "district": "Surat", "total_students": 4750, "udise_code": "24190100777"},
            {"school_name": "Maharaja Sayajirao Model Vidyalaya", "district": "Vadodara", "total_students": 4520, "udise_code": "24190200666"},
            {"school_name": "Saurashtra State Premier High School", "district": "Rajkot", "total_students": 4310, "udise_code": "24090100555"},
        ]
        session.bulk_insert_mappings(School, top_anchor_schools)
        session.commit()
        remaining -= len(top_anchor_schools)

    # Bulk insert generation with guaranteed unique UDISE code
    added = 0
    while added < remaining:
        current_batch_size = min(batch_size, remaining - added)
        batch = []
        for i in range(current_batch_size):
            district_idx = (existing_count + added + i) % len(districts)
            district = districts[district_idx]
            prefix = random.choice(SCHOOL_PREFIXES)
            area = random.choice(AREAS)
            name = f"{prefix} - {area}, {district}"
            students = random.randint(80, 4200)
            # Mathematically guaranteed unique 11-digit UDISE format
            udise = f"24{district_idx:02d}{existing_count + added + i:07d}"
            batch.append({
                "school_name": name,
                "district": district,
                "total_students": students,
                "udise_code": udise
            })

        session.bulk_insert_mappings(School, batch)
        session.commit()
        added += current_batch_size
        print(f"Inserted {added}/{remaining} records...")

    total = session.query(School).count()
    session.close()
    print(f"Successfully seeded! Total schools in database now: {total}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed Gujarat Schools Dataset")
    parser.add_argument("--count", type=int, default=50000, help="Target total schools count")
    args = parser.parse_args()
    seed_large_school_dataset(target_count=args.count)
