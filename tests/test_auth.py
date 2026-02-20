from app.services.auth_service import AuthService


def test_login_success(client, user):
    resp = client.post('/api/auth/login', json={'email': 'test@example.com', 'password': 'secret'})
    assert resp.status_code == 200
    data = resp.get_json()
    assert 'access_token' in data
    assert data['user']['email'] == 'test@example.com'


def test_login_failure(client):
    resp = client.post('/api/auth/login', json={'email': 'noone@example.com', 'password': 'x'})
    assert resp.status_code == 401


def test_logout_and_validate_session(client, user):
    resp = client.post('/api/auth/login', json={'email': 'test@example.com', 'password': 'secret'})
    assert resp.status_code == 200
    token = resp.get_json()['access_token']

    # Session should be valid
    assert AuthService.validate_session(token) is True

    # Logout via endpoint
    headers = {'Authorization': f'Bearer {token}'}
    resp2 = client.post('/api/auth/logout', headers=headers)
    assert resp2.status_code == 200

    # Session should now be invalid
    assert AuthService.validate_session(token) is False
