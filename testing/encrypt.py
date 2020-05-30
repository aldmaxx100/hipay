import json
from base64 import b64encode,b64decode
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.Random import get_random_bytes
data = '8652881964@#@150@#@gxxn5@funny@#@5147@#@uiopy08'
data=bytes(data, 'utf-8')
print(data)
shared='XTKrD3becHyeFzXBWKfYa81E2j7wJCqwtzRELnQf0Ko='
key=b64decode(shared)
cipher = AES.new(key, AES.MODE_CBC)
ct_bytes = cipher.encrypt(pad(data, AES.block_size))
iv = b64encode(cipher.iv).decode('utf-8')
ct = b64encode(ct_bytes).decode('utf-8')
print(len(iv))
print(len(ct))
result = json.dumps({'iv':iv, 'ct':ct})
print(result)