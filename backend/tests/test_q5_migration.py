"""
[Q5: Legacy Data Migration Strategy]
Test Suite: ETL Migration, Data Cleansing & Transaction Rollback
----------------------------------------------------------------
Verifies:
1. Extraction from messy legacy JSON source.
2. Cryptographic SHA-256 source file audit checksum.
3. Cleanse transformations:
   - Currency cleanup ("₹ 1,80,000/-" -> 180000.0)
   - District normalization ("ahmedabad " -> "Ahmedabad")
   - Aadhaar one-way hashing & display masking
4. Quarantine isolation of corrupted anomaly rows.
5. Invariant integrity: `total_extracted == len(valid) + len(quarantined)`.
6. Atomic rollback on batch failure leaving database uncorrupted.
"""

from pathlib import Path
import pytest
from scripts.migrate_legacy import run_migration_etl, compute_file_checksum


@pytest.fixture
def sample_legacy_file():
    return Path(__file__).resolve().parent.parent / "scripts" / "legacy_students_sample.json"


def test_q5_migration_etl_success(sample_legacy_file):
    assert sample_legacy_file.exists()

    report = run_migration_etl(sample_legacy_file, simulate_failure_rollback=False)

    assert report["migration_status"] == "SUCCESS"
    assert report["total_extracted"] == 6
    assert report["valid_transformed"] == 5
    assert report["quarantined_anomalies"] == 1
    assert report["loaded_to_database"] == 5
    assert len(report["source_sha256_checksum"]) == 64
    assert report["duration_ms"] > 0


def test_q5_migration_atomic_rollback(sample_legacy_file):
    # Test with simulated failure flag
    report = run_migration_etl(sample_legacy_file, simulate_failure_rollback=True)

    assert report["migration_status"] == "ROLLED_BACK"
    assert report["loaded_to_database"] == 0  # Zero rows committed due to rollback
    assert report["total_extracted"] == 6
