from ecg.db import get_connection_string, ping


def test_connection_string_present():
    assert get_connection_string().startswith("postgresql://")


def test_database_is_reachable():
    assert ping() is True
