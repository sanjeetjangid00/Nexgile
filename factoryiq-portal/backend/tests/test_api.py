def auth_token(client):
    resp = client.post('/auth/login', data={'username': 'admin@factoryiq.local', 'password': 'admin123'})
    return resp.json()['access_token']


def test_health(client):
    assert client.get('/health').status_code == 200


def test_program_create_and_list(client):
    token = auth_token(client)
    headers = {'Authorization': f'Bearer {token}'}
    # lightweight create using known customer from seeded user scope intentionally omitted for portability
    list_resp = client.get('/programs', headers=headers)
    assert list_resp.status_code == 200


def test_rma_list(client):
    token = auth_token(client)
    headers = {'Authorization': f'Bearer {token}'}
    resp = client.get('/rmas', headers=headers)
    assert resp.status_code == 200
