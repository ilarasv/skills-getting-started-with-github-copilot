from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

ORIGINAL_ACTIVITIES = deepcopy(activities)
client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    activities.clear()
    activities.update(deepcopy(ORIGINAL_ACTIVITIES))
    yield
    activities.clear()
    activities.update(deepcopy(ORIGINAL_ACTIVITIES))


def test_get_activities_returns_activity_data():
    response = client.get("/activities")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert data["Chess Club"]["schedule"] == "Fridays, 3:30 PM - 5:00 PM"


def test_signup_adds_participant_to_activity():
    email = "test.student@mergington.edu"
    response = client.post("/activities/Soccer%20Team/signup?email=test.student%40mergington.edu")

    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for Soccer Team"
    assert email in activities["Soccer Team"]["participants"]


def test_signup_duplicate_email_returns_400():
    email = "emma@mergington.edu"
    response = client.post(f"/activities/Programming%20Class/signup?email={email}")
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_remove_participant_from_activity():
    email = "michael@mergington.edu"
    response = client.delete(f"/activities/Chess%20Club/signup?email={email}")

    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {email} from Chess Club"
    assert email not in activities["Chess Club"]["participants"]


def test_remove_missing_participant_returns_404():
    email = "not.registered@mergington.edu"
    response = client.delete(f"/activities/Soccer%20Team/signup?email={email}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"


def test_unknown_activity_returns_404_for_signup_and_remove():
    signup_response = client.post("/activities/Unknown%20Club/signup?email=user%40example.com")
    remove_response = client.delete("/activities/Unknown%20Club/signup?email=user%40example.com")

    assert signup_response.status_code == 404
    assert signup_response.json()["detail"] == "Activity not found"
    assert remove_response.status_code == 404
    assert remove_response.json()["detail"] == "Activity not found"
