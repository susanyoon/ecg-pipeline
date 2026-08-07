from ecg.labels import superclasses_for_record


def test_maps_codes_to_superclasses():
    mapping = {"NORM": "NORM", "IMI": "MI", "ASMI": "MI"}
    codes = {"NORM": 100.0, "IMI": 80.0}
    assert superclasses_for_record(codes, mapping) == ["MI", "NORM"]


def test_dedupes_superclasses():
    mapping = {"IMI": "MI", "ASMI": "MI"}
    codes = {"IMI": 100.0, "ASMI": 50.0}
    # both map to MI -> single entry
    assert superclasses_for_record(codes, mapping) == ["MI"]


def test_ignores_non_diagnostic_codes():
    mapping = {"NORM": "NORM"}  # SR not in the diagnostic map
    codes = {"NORM": 100.0, "SR": 0.0}
    assert superclasses_for_record(codes, mapping) == ["NORM"]


def test_empty_when_no_diagnostic_codes():
    mapping = {"NORM": "NORM"}
    codes = {"SR": 0.0, "LVOLT": 0.0}
    assert superclasses_for_record(codes, mapping) == []
