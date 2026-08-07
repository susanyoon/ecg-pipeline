from ecg.download import METADATA_FILES


def test_metadata_file_list():
    # a cheap structural tesst that does NOT hit the network.
    assert "ptbxl_database.csv" in METADATA_FILES
    assert "scp_statements.csv" in METADATA_FILES
