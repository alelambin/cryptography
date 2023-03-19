from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad


BLOCK_SIZE = 16


def encrypt(plaintext, key, iv=bytes(BLOCK_SIZE)):
    return AES.new(key, AES.MODE_CBC, iv).encrypt(pad(plaintext.encode('utf-8'), BLOCK_SIZE))


def decrypt(ciphertext, key, iv=bytes(BLOCK_SIZE)):
    return unpad(AES.new(key, AES.MODE_CBC, iv).decrypt(ciphertext), BLOCK_SIZE).decode('utf-8')
