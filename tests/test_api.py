"""Automated test suite for Space Bounty Hunters REST API."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models import HuntLog, WantedCriminal

# In-memory SQLite for instantaneous automated testing
TEST_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(
    bind=test_engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_database():
    """Create fresh tables and seed test data before each test."""
    Base.metadata.create_all(bind=test_engine)
    session = TestingSessionLocal()

    # Seed 5 criminals
    c1 = WantedCriminal(
        id=1,
        name="Vicious Kane",
        nickname="Red Nova",
        reward=150000.0,
        last_known_coordinates="Kepler-22b (-14.2, 120.4)",
        difficulty=9,
        armed=True,
        has_crew=True,
        escape_master=True,
    )
    c2 = WantedCriminal(
        id=2,
        name="Lyra Vance",
        nickname="Silver Ghost",
        reward=85000.0,
        last_known_coordinates="Ganymede Bay 9",
        difficulty=7,
        armed=True,
        has_crew=False,
        escape_master=True,
    )
    c3 = WantedCriminal(
        id=3,
        name=None,
        nickname="Obsidian Raven",
        reward=220000.0,
        last_known_coordinates="Kuiper Outpost 88",
        difficulty=10,
        armed=True,
        has_crew=True,
        escape_master=True,
    )
    c4 = WantedCriminal(
        id=4,
        name="Jaxson Miller",
        nickname="Plasma Jack",
        reward=45000.0,
        last_known_coordinates="Mars Cydonia Block 14-C",
        difficulty=5,
        armed=True,
        has_crew=False,
        escape_master=False,
    )
    c5 = WantedCriminal(
        id=5,
        name="Corinne Dubois",
        nickname="Viper Queen",
        reward=120000.0,
        last_known_coordinates="Europa Sub-ice",
        difficulty=8,
        armed=False,
        has_crew=True,
        escape_master=False,
    )
    session.add_all([c1, c2, c3, c4, c5])
    session.commit()

    # Seed 10 hunt logs
    logs = [
        HuntLog(id=1, criminal_id=1, success=False, notes="Kepler ambush"),
        HuntLog(id=2, criminal_id=1, success=False, notes="Asteroid belt skirmish"),
        HuntLog(id=3, criminal_id=2, success=False, notes="Ganymede lock hack"),
        HuntLog(id=4, criminal_id=2, success=True, notes="Captured in cryo-stasis"),
        HuntLog(id=5, criminal_id=3, success=False, notes="Decoy drone mirrored signature"),
        HuntLog(id=6, criminal_id=3, success=False, notes="Ice tunnel shootout"),
        HuntLog(id=7, criminal_id=4, success=True, notes="Captured at Mars bazaar"),
        HuntLog(id=8, criminal_id=5, success=False, notes="Sub-ice submarine toxic gas"),
        HuntLog(id=9, criminal_id=5, success=False, notes="Syndicate reinforcements"),
        HuntLog(id=10, criminal_id=4, success=False, notes="Earlier attempt on Phobos"),
    ]
    session.add_all(logs)
    session.commit()
    session.close()

    yield

    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def client():
    return TestClient(app)


# -----------------------------------------------------------------------------
# Wanted Criminals API Tests
# -----------------------------------------------------------------------------
def test_list_all_criminals(client):
    res = client.get("/api/criminals/")
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 5
    assert data[0]["nickname"] == "Red Nova"


def test_filter_and_sort_criminals_example(client):
    # Assignment example: /api/criminals/?min_reward=5000&armed=true&sort=-reward
    res = client.get("/api/criminals/?min_reward=5000&armed=true&sort=-reward")
    assert res.status_code == 200
    data = res.json()
    # Armed criminals: c1 (150k), c2 (85k), c3 (220k), c4 (45k). All > 5000
    assert len(data) == 4
    # Check descending sort by reward: 220000, 150000, 85000, 45000
    rewards = [item["reward"] for item in data]
    assert rewards == [220000.0, 150000.0, 85000.0, 45000.0]
    for item in data:
        assert item["armed"] is True
        assert item["reward"] >= 5000


def test_filter_crew_and_max_reward(client):
    res = client.get("/api/criminals/?max_reward=130000&has_crew=true")
    assert res.status_code == 200
    data = res.json()
    # c5: reward 120000, has_crew True
    assert len(data) == 1
    assert data[0]["nickname"] == "Viper Queen"


def test_filter_escape_master_and_sort_asc(client):
    res = client.get("/api/criminals/?escape_master=true&sort=reward")
    assert res.status_code == 200
    data = res.json()
    # c2 (85k), c1 (150k), c3 (220k)
    rewards = [item["reward"] for item in data]
    assert rewards == [85000.0, 150000.0, 220000.0]


def test_invalid_sort_parameter(client):
    res = client.get("/api/criminals/?sort=invalid")
    assert res.status_code == 400
    assert "Invalid sort" in res.json()["detail"]


def test_get_criminal_details(client):
    res = client.get("/api/criminals/1/")
    assert res.status_code == 200
    data = res.json()
    assert data["id"] == 1
    assert data["nickname"] == "Red Nova"
    assert "hunt_logs" in data
    assert len(data["hunt_logs"]) == 2


def test_get_criminal_not_found(client):
    res = client.get("/api/criminals/99999/")
    assert res.status_code == 404
    assert "not found" in res.json()["detail"].lower()


# -----------------------------------------------------------------------------
# Bounty Hunting Journal (HuntLog CRUD) Tests
# -----------------------------------------------------------------------------
def test_list_all_hunts(client):
    res = client.get("/api/hunts/")
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 10


def test_filter_hunts_by_criminal_id(client):
    res = client.get("/api/hunts/?criminal_id=1")
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 2
    for log in data:
        assert log["criminal_id"] == 1


def test_get_one_hunt(client):
    res = client.get("/api/hunts/1/")
    assert res.status_code == 200
    data = res.json()
    assert data["id"] == 1
    assert data["criminal_id"] == 1
    assert "created_at" in data


def test_get_hunt_not_found(client):
    res = client.get("/api/hunts/99999/")
    assert res.status_code == 404


def test_create_hunt_success(client):
    body = {
        "criminal_id": 3,
        "success": False,
        "notes": "Target escaped through an asteroid field.",
    }
    res = client.post("/api/hunts/", json=body)
    assert res.status_code == 201
    data = res.json()
    assert data["criminal_id"] == 3
    assert data["success"] is False
    assert data["notes"] == "Target escaped through an asteroid field."
    assert "created_at" in data
    assert data["id"] is not None


def test_create_hunt_invalid_criminal_reference(client):
    body = {
        "criminal_id": 99999,
        "success": False,
        "notes": "Attempt against ghost target.",
    }
    res = client.post("/api/hunts/", json=body)
    assert res.status_code == 404
    assert "does not exist" in res.json()["detail"].lower()


def test_patch_hunt(client):
    update_body = {
        "success": True,
        "notes": "Target finally captured after secondary tracking.",
    }
    res = client.patch("/api/hunts/1/", json=update_body)
    assert res.status_code == 200
    data = res.json()
    assert data["id"] == 1
    assert data["success"] is True
    assert data["notes"] == "Target finally captured after secondary tracking."


def test_patch_hunt_empty_body(client):
    res = client.patch("/api/hunts/1/", json={})
    assert res.status_code == 400


def test_patch_hunt_not_found(client):
    res = client.patch("/api/hunts/99999/", json={"success": True})
    assert res.status_code == 404


def test_delete_hunt(client):
    del_res = client.delete("/api/hunts/1/")
    assert del_res.status_code == 204

    # Verify it is deleted
    get_res = client.get("/api/hunts/1/")
    assert get_res.status_code == 404


def test_delete_hunt_not_found(client):
    res = client.delete("/api/hunts/99999/")
    assert res.status_code == 404
