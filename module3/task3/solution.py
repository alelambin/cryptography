def encrypt_CBC(plaintext, key, iv=bytes(8)):
    BLOCK_SIZE = 8
    block_index = 0
    length = len(plaintext)
    ciphertext = b''
    prev_block = iv
    while block_index < length:
        block = plaintext[block_index : block_index + BLOCK_SIZE] \
            if block_index + BLOCK_SIZE <= length \
            else plaintext[block_index : length] + bytes([0] * (BLOCK_SIZE - (length - block_index)))
        new_block = encrypt_block(bytes([_1 ^ _2 for _1, _2 in zip(prev_block, block)]), key)
        ciphertext += new_block
        prev_block = new_block 
        block_index += BLOCK_SIZE
    return ciphertext
