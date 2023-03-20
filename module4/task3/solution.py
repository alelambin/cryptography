def encrypt(plaintext, e, n):
    ciphertext = []
    for byte in plaintext:
        ciphertext.append(ord(byte) ** e % n)
    return ciphertext


def decrypt(ciphertext, d, n):
    plaintext = ''
    for byte in ciphertext:
        plaintext += chr(byte ** d % n)
    return plaintext
