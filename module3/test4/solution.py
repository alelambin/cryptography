from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad


BLOCK_SIZE = 16

key = b'A1B2C3D4E5F6G7H8'
iv = b'0000000000000000'

cipher = AES.new(key, AES.MODE_CBC, iv=iv)
plaintext = b'Python'
ciphertext = cipher.encrypt(pad(plaintext, BLOCK_SIZE))
print(ciphertext)

cipher = AES.new(key, AES.MODE_CBC, iv=iv)
plaintext = unpad(cipher.decrypt(ciphertext), BLOCK_SIZE)
print(plaintext.decode('utf-8'))
