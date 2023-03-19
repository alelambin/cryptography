def encrypt_ECB(plaintext, key):
    BLOCK_SIZE = 8
    block_index = 0
    length = len(plaintext)
    ciphertext = b''
    while block_index < length:
        block = plaintext[block_index : block_index + BLOCK_SIZE] if block_index + BLOCK_SIZE <= length else plaintext[block_index : length] + bytes([0] * (BLOCK_SIZE - (length - block_index)))
        ciphertext += encrypt_block(block, key)
        block_index += BLOCK_SIZE
    return ciphertext
