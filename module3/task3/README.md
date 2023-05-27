Имеется функция `encrypt_block(plain_block, key)`, принимающая на вход блок открытого текста `plain_block` (`bytes`) длины 64 бит и ключ `key` (`bytes`) длины 64 бит и возвращающая блок шифротекста (`bytes`). Реализуйте функцию `encrypt_CBC(plaintext, key, iv=bytes(8))` (`iv` – вектор инициализации), реализующую шифрование в режиме CBC без использования `PyCryptodome`.

Блок открытого тектса, при необходимости, дополните нулями.

| Входные данные | Выходные данные |
| --- | --- |
| `encrypt_CBC(b'12345678', b'-KEYKEY-')` | `b'&\xf3\xa1l\xbfX\xef\xcb'` |
| `encrypt_CBC(b'12345678', b'-KEYKEY-', b'12345678')` | `b'\x12\xe7\xf8\x9fc\xa8\x02U'` |
| `encrypt_CBC(b'', b'-KEYKEY-')` | `b''` |
