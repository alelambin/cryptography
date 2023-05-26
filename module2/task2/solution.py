ALPHABET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'


def decrypt(ciphertext, key):
    plaintext = ''
    for letter in ciphertext:
        plaintext += ALPHABET[(ord(letter) - 65 - key) % len(ALPHABET)]
    return plaintext
