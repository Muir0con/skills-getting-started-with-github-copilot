from copy import deepcopy
from urllib.parse import quote

from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)
initial_activities = deepcopy(activities)


def reset_activities():
    activities.clear()
    activities.update(deepcopy(initial_activities))


def test_get_activities():
    # Arrange
    reset_activities()

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert isinstance(data["Chess Club"]["participants"], list)
    assert data["Chess Club"]["max_participants"] == 12


def test_signup_for_activity():
    # Arrange
    reset_activities()
    activity_name = "Chess Club"
    email = "teststudent@mergington.edu"
    assert email not in activities[activity_name]["participants"]
    path = f"/activities/{quote(activity_name)}/signup"

    # Act
    response = client.post(path, params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}
    assert email in activities[activity_name]["participants"]


def test_duplicate_signup_returns_400():
    # Arrange
    reset_activities()
    activity_name = "Chess Club"
    email = "duplicate@mergington.edu"
    path = f"/activities/{quote(activity_name)}/signup"

    response = client.post(path, params={"email": email})
    assert response.status_code == 200

    # Act
    duplicate_response = client.post(path, params={"email": email})

    # Assert
    assert duplicate_response.status_code == 400
    assert duplicate_response.json()["detail"] == "Student already signed up for this activity"


def test_unregister_participant():
    # Arrange
    reset_activities()
    activity_name = "Chess Club"
    email = "michael@mergington.edu"
    assert email in activities[activity_name]["participants"]
    path = f"/activities/{quote(activity_name)}/participants"

    # Act
    response = client.delete(path, params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {email} from {activity_name}"}
    assert email not in activities[activity_name]["participants"]


def test_unregister_missing_participant_returns_404():
    # Arrange
    reset_activities()
    activity_name = "Chess Club"
    email = "not-registered@mergington.edu"
    path = f"/activities/{quote(activity_name)}/participants"

    # Act
    response = client.delete(path, params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not registered for this activity"
