import pytest


@pytest.mark.integration
def test_insert_and_find_user(mongo_db):
    users = mongo_db["users"]
    users.insert_one({"name": "Alice", "approved": True})
    doc = users.find_one({"name": "Alice"})
    assert doc is not None
    assert doc["approved"] is True
