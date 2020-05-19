import json
from base64 import b64decode
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
shared='ZYDq8iOox2Tko3MHVkBDCpZzqAn/mkoQKDhHYc9lxyk='
json_input='{"iv": "BpRPsjhCn9Jsz5z15AuAgA==", "ciphertext": "S0u4B04RSsw6XMBQMFR86b1m/GRpTHkvlx+A0ASlmXk="}'
key=b64decode(shared)
try:
     b64 = json.loads(json_input)
     iv = b64decode(b64['iv'])
     ct = b64decode(b64['ciphertext'])
     cipher = AES.new(key, AES.MODE_CBC, iv)
     pt = unpad(cipher.decrypt(ct), AES.block_size)
     print("The message was: ", pt.decode('utf-8'))
except Exception as e:
     print("Incorrect decryption")