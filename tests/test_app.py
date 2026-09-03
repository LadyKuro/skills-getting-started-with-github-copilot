from src import app as app_module


class TestRoot:
    def test_root_redirects_to_frontend(self, client):
        # Arrange
        expected_location = "/static/index.html"

        # Act
        response = client.get("/", follow_redirects=False)

        # Assert
        assert response.status_code == 307
        assert response.headers["location"] == expected_location


class TestActivities:
    def test_get_activities_returns_activity_data(self, client):
        # Arrange
        expected_participants = [
            "michael@mergington.edu",
            "daniel@mergington.edu",
        ]

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        assert response.json()["Chess Club"]["participants"] == expected_participants


class TestSignup:
    def test_signup_adds_participant(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "new.student@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 200
        assert response.json() == {
            "message": f"Signed up {email} for {activity_name}"
        }
        assert email in app_module.activities[activity_name]["participants"]

    def test_signup_rejects_duplicate_participant(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        initial_count = app_module.activities[activity_name]["participants"].count(email)

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Student already signed up for this activity"
        assert app_module.activities[activity_name]["participants"].count(email) == initial_count

    def test_signup_rejects_unknown_activity(self, client):
        # Arrange
        activity_name = "Unknown Club"
        email = "new.student@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"


class TestUnregister:
    def test_unregister_removes_participant(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"

        # Act
        response = client.delete(f"/activities/{activity_name}/participants/{email}")

        # Assert
        assert response.status_code == 200
        assert response.json() == {
            "message": f"Unregistered {email} from {activity_name}"
        }
        assert email not in app_module.activities[activity_name]["participants"]

    def test_unregister_rejects_missing_participant(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "missing.student@mergington.edu"

        # Act
        response = client.delete(f"/activities/{activity_name}/participants/{email}")

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Student is not signed up for this activity"

    def test_unregister_rejects_unknown_activity(self, client):
        # Arrange
        activity_name = "Unknown Club"
        email = "student@mergington.edu"

        # Act
        response = client.delete(f"/activities/{activity_name}/participants/{email}")

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_activity_state_is_reset_between_tests(self, client):
        # Arrange
        activity_name = "Soccer Club"
        email = "isolated.student@mergington.edu"
        assert email not in app_module.activities[activity_name]["participants"]

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 200
        assert email in app_module.activities[activity_name]["participants"]
