from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)

START_ACTIVITIES = None


def setup_function(function):
    global START_ACTIVITIES
    if START_ACTIVITIES is None:
        START_ACTIVITIES = {
            k: {
                **v,
                'participants': list(v['participants'])
            }
            for k, v in activities.items()
        }
    activities.clear()
    activities.update({
        k: {
            **v,
            'participants': list(v['participants'])
        }
        for k, v in START_ACTIVITIES.items()
    })


def test_get_activities():
    # Arrange
    # Act
    res = client.get('/activities')
    # Assert
    assert res.status_code == 200
    data = res.json()
    assert 'Chess Club' in data
    assert 'Music Band' in data


def test_signup_for_activity_success():
    # Arrange
    email = 'newstudent@mergington.edu'
    # Act
    res = client.post(f"/activities/{'Chess Club'}/signup?email={email}")
    # Assert
    assert res.status_code == 200
    assert 'Signed up' in res.json()['message']
    assert email in activities['Chess Club']['participants']


def test_signup_duplicate_returns_400():
    # Arrange
    email = 'daniel@mergington.edu'
    # Act
    res1 = client.post(f"/activities/{'Chess Club'}/signup?email={email}")
    res2 = client.post(f"/activities/{'Chess Club'}/signup?email={email}")
    # Assert
    assert res1.status_code in (200, 400)
    assert res2.status_code == 400


def test_signup_full_activity_returns_400():
    # Arrange
    activities['Test Club'] = {
        'description': 'A test club',
        'schedule': 'Now',
        'max_participants': 1,
        'participants': ['already@mergington.edu']
    }
    # Act
    res = client.post('/activities/Test Club/signup?email=full@mergington.edu')
    # Assert
    assert res.status_code == 400


def test_remove_participant_success():
    # Arrange
    email = 'michael@mergington.edu'
    # Act
    res = client.delete(f"/activities/{'Chess Club'}/participants/{email}")
    # Assert
    assert res.status_code == 200
    assert email not in activities['Chess Club']['participants']


def test_remove_participant_not_found_returns_404():
    # Arrange
    email = 'noone@mergington.edu'
    # Act
    res = client.delete(f"/activities/{'Chess Club'}/participants/{email}")
    # Assert
    assert res.status_code == 404
