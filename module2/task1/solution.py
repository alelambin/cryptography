ALPHABET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'


def encrypt(plaintext, key):
    ciphertext = ''
    for letter in plaintext:
        ciphertext += ALPHABET[(ord(letter) - 65 + key) % len(ALPHABET)]
    return ciphertext
