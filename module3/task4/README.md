Алиса и Боб теперь знают, что шифр Цезаря очень легко взломать, поэтому для шифрования сообщений было принято использовать алгоритм AES в режиме CBC. Реализуйте функции `encrypt(plaintext, key, iv=bytes(16))`, возвращающую массив байт, и `decrypt(ciphertext, key, iv=bytes(16))`, возвращающую строку, для шифрования и расшифровки сообщений. Функции принимают на вход строку `plaintext` и массив байт `ciphertext`. В данном задании воспользуйтесь готовой реализацией алгоритма из модуля `Crypto.Cipher`. Не забудьте проверить валидность ключа.

В качестве алгоритма дополнения используйте `pkcs7`.

| Входные данные | Выходные данные |
| --- | --- |
| `encrypt('ABCDEFGHIJKLMNOP', b'-16B-SECRET-KEY-')` <br> `decrypt(b"\x95<\x99\x9d\x98EL\xad\xf8%\x03\xb7\x0c\xd3~\xe2*'\xec\xe9a7\xe3\xf54\x04\x1eM\xceW\x99\xf0", b'-16B-SECRET-KEY-')` | `b"\x95<\x99\x9d\x98EL\xad\xf8%\x03\xb7\x0c\xd3~\xe2*'\xec\xe9a7\xe3\xf54\x04\x1eM\xceW\x99\xf0"` <br> `'ABCDEFGHIJKLMNOP'` |
| `encrypt('ABCDEFGHIJKLMNOP', b'-----24B-SECRET-KEY-----')` <br> `decrypt(b'xR\xd3\x84\x08\x99\x90\xe2\xae\xdb\xf3\x93\xed\|\x9bm\xca\xa6A\xd7\xec\x13d\xbbq\x11\xbd\xd6\xbe\xa8\x99A', b'-----24B-SECRET-KEY-----')` | `b'xR\xd3\x84\x08\x99\x90\xe2\xae\xdb\xf3\x93\xed\|\x9bm\xca\xa6A\xd7\xec\x13d\xbbq\x11\xbd\xd6\xbe\xa8\x99A'` <br> `'ABCDEFGHIJKLMNOP'` |
| `encrypt('', b'-16B-SECRET-KEY-')` <br> `decrypt(b'\x9e\xe1H\xad2\x1fw\x96\x934\xad\x0cQ\x03zz', b'-16B-SECRET-KEY-')` | `b'\x9e\xe1H\xad2\x1fw\x96\x934\xad\x0cQ\x03zz'` <br> `''` |
