import json
from base64 import b64encode,b64decode
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.Random import get_random_bytes
data = '9224695147@#@150@#@sijs8@funny@#@4778'
data=bytes(data, 'utf-8')
print(data)
shared='PLihShLEhg+uQrKnTfNUQr62hp4SJkiVhiq77nIe6Xk='
key=b64decode(shared)
cipher = AES.new(key, AES.MODE_CBC)
ct_bytes = cipher.encrypt(pad(data, AES.block_size))
iv = b64encode(cipher.iv).decode('utf-8')
ct = b64encode(ct_bytes).decode('utf-8')
print(len(iv))
print(len(ct))
result = json.dumps({'iv':iv, 'ct':ct})
print(result)