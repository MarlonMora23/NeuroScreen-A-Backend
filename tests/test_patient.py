def test_create_get_update_delete_patient(client, user):
    # Login to obtain token
    resp = client.post('/api/auth/login', json={'email': 'test@example.com', 'password': 'secret'})
    assert resp.status_code == 200
    token = resp.get_json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}

    # Create patient
    payload = {'identification_number': 'ID123', 'first_name': 'Ana', 'last_name': 'Perez'}
    r = client.post('/api/patients', json=payload, headers=headers)
    assert r.status_code == 201
    patient = r.get_json()
    assert patient['identification_number'] == 'ID123'
    pid = patient['id']

    # Get patient
    r2 = client.get(f'/api/patients/{pid}', headers=headers)
    assert r2.status_code == 200

    # Update patient
    r3 = client.put(f'/api/patients/{pid}', json={'first_name': 'Ana Maria'}, headers=headers)
    assert r3.status_code == 200
    assert r3.get_json()['first_name'] == 'Ana Maria'

    # Delete patient
    r4 = client.delete(f'/api/patients/{pid}', headers=headers)
    assert r4.status_code == 200
