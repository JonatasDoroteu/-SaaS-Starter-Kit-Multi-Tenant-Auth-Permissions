import json
import urllib.error
import urllib.request

req = urllib.request.Request(
    'http://127.0.0.1:8001/api/v1/auth/login',
    data=json.dumps({'email': 'demo@example.com', 'password': 'secret123'}).encode(),
    headers={'Content-Type': 'application/json'},
    method='POST',
)

try:
    with urllib.request.urlopen(req) as response:
        print(response.status)
        print(response.read().decode())
except urllib.error.HTTPError as exc:
    print('HTTP', exc.code)
    print(exc.read().decode())
