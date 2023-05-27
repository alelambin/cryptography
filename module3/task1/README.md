Имеется функция `encrypt_block(plain_block, key)`, принимающая на вход блок открытого текста `plain_block` (`bytes`) длины 64 бит и ключ `key` (`bytes`) длины 64 бит и возвращающая блок шифротекста (`bytes`). Реализуйте функцию `encrypt_ECB(plaintext, key)`, реализующую шифрование в режиме ECB без использования `PyCryptodome`. 

Блок открытого тектса, при необходимости, дополните нулями.

| Входные данные | Выходные данные |
| --- | --- |
| `encrypt_ECB(b'12345678', b'-KEYKEY-')` | `b'&\xf3\xa1l\xbfX\xef\xcb'` |
| `encrypt_ECB(b'1234567812345678', b'-KEYKEY-')` | `b'&\xf3\xa1l\xbfX\xef\xcb&\xf3\xa1l\xbfX\xef\xcb'` |
| `encrypt_ECB(b'1234567890', b'-KEYKEY-')` | `b'&\xf3\xa1l\xbfX\xef\xcb\xeb\x16\x11\xf7X\xa2X\xf1'` |
