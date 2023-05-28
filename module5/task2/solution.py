from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA3_512


def sign(message):
    key = RSA.generate(1024)
    digest = SHA3_512.new(message)
    return (pkcs1_15.new(key).sign(digest), key.public_key())
