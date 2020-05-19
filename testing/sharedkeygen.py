import secrets
from base64 import b64encode
key=secrets.token_bytes(32)


shared=b64encode(key).decode('utf-8')
print('sharedkey is')
print(shared)