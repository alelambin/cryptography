from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA


def encrypt(plain_block_key, public_key_filename):
    with open(public_key_filename, 'rb') as file:
        key = RSA.import_key(file.read())
    return PKCS1_OAEP.new(key).encrypt(plain_block_key)


def decrypt(cipher_block_key, private_key_filename):
    with open(private_key_filename, 'rb') as file:
        key = RSA.import_key(file.read())
    return PKCS1_OAEP.new(key).decrypt(cipher_block_key)
