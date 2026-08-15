import os

import pytest

os.environ["DATABASE_URL"] = "postgresql://ecg:ecg_password@localhost:5432/ecg_test"

@pytest.fixture(scope="session", autouse=True)
def _create_schema():
    """Ensure the test database has the schema before any test runs."""
    from ecg.db import init_schema

    init_schema()
