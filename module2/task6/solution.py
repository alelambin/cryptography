ALPHABET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'


def decrypt(ciphertext, key):
    plaintext = ''
    for letter in ciphertext:
        plaintext += ALPHABET[(ord(letter) - 65 - key) % len(ALPHABET)]
    return plaintext


def hack(ciphertext):
    plaintext = ''
    key = 0
    for i in range(len(ALPHABET)):
        if decrypt(ciphertext[-5:], i) == 'ALICE':
            key = i
            break
    return decrypt(ciphertext, key)
