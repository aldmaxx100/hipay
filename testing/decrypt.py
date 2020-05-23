import json
from base64 import b64decode
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
shared='P4So8XHEz+VqxG5bb1XwrLEO4Lcdf5dvbjRFllKZRPE='
json_input='{"iv": "H1MrxlXnj9EhlDNfSzr0Ig==", "ciphertext": "VNy+TD14zse5xm9qdXHMJpNVBi1WhMm3p1ZWKKEV5rclgddzvLqpWEUrKmf3bBWQU1IxItshFVnsCCiPysHAvw=="}'
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