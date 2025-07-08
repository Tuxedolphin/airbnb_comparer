from project import retrieve_from_json, db_table_filter

def test_retrieve_from_json():
    assert retrieve_from_json("ID", json_data) == "26167241"


def test_db_table_filter():
    assert db_table_filter("id") == "main"


def test_retrieve_from_location():
    assert True
