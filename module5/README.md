# 5. Хэш-функции

Шифрование данных позволяет передавать информацию по незащищённым каналам связи, однако оно не позволяет определить целостность данных и подлинность отправителя. В процессе передачи нарушитель может воздействовать на передаваемую информацию. Чтобы обезопасить себя можно воспользоваться кодами аутентификации. Прежде, чем рассматривать коды аутентификации, необходимо рассмотреть понятие хэш-функции.

**Хэш-функцией** называется такая функция, которая для строки бит произвольной длины вычисляет некоторую другую строку бит фиксированной длины, так называемый **хэш**, **хэш-код**, **хэш-сумма** или **дайджест**. В криптографии используются криптографические хэш-функции – такие хэш-функции $H (x)$, на которые дополнительно накладываются следующие ограничения:
- устойчивость к прообразам (для заданного $h$ вычислительно трудно найти значение $x = H^{-1} (h)$);
- устойчивость к второму прообразу (для заданного $x$ вычислительно трудно подобрать такой $y \ne x$, что $H (y) = H (x)$);
- устойчивость к коллизиям (вычислительно трудно подобрать пару $(x, y)$, что $x \ne y$ и $H (x) = H (y)$).

Одной из важных характеристик алгоритмов хэширования является размер выходного хэш-кода. Так, например, у хэш-функции [**MD5**](https://ru.wikipedia.org/wiki/MD5) размер хэш-кода составляет 128 бит, у [**SHA-1**](https://ru.wikipedia.org/wiki/SHA-1) – 160 бит, у [**SHA-3**](https://ru.wikipedia.org/wiki/SHA-3) длина хэш-кода может быть переменной длины.

```python
from Crypto.Hash import SHA1


message = b'Python'
digest = SHA1.new(message)
print(digest.hexdigest())
digest.update(b'Python3')
print(digest.hexdigest())

print(hash('Python'))

```

Хэш-функции можно импортировать из модуля `Crypto.Hash`. Заметьте, что с помощью метода `update()` можно менять входную последовательность бит. Чтобы вывести результат, можно воспользоваться методом `hexdigest()`, возвращающим последовательность в 16-ричном представлении. Запустив данный код можно заметить, что изменение даже одного бита приводит к изменению всего хэш-кода.

В Python имеется встроенная функция вычисления значения хэша `hash()`. Данная хэш-функция не является криптографической, позволяет использовать хэш, например, для быстрого сравнения ключей словаря. Однако Python имеет стандартный модуль с криптографическими хэш-функциями [`hashlib`](https://docs-python.ru/standart-library/modul-hashlib-python/).

Одно из применений хэш-функций – контроль целостности и аутентификация отправителя. Базовый алгоритм был рассмотрен в первом модуле. Однако встаёт вопрос, как передать хэш-код другой стороне. Если передавать его по открытому каналу связи, то нарушитель сможет изменить как сообщение, так и хэш-код, что не позволит решить поставленные задачи. 

Решением являются **коды аутентификации** (**message authentication code** или **MAC**). Основная идея заключается в вычислении хэш-суммы от сообщения и некоторого симметричного ключа. Поскольку нарушитель не имеет доступа к симметричному ключу, подделать хэш-код он не сможет.

Существует несколько способов вычисления MAC. Одними из них являются [**HMAC**](https://ru.wikipedia.org/wiki/HMAC) и [**CMAC**](https://ru.wikipedia.org/wiki/CBC-MAC). 

Создать HMAC с помощью PyCryptodome можно следующим образом:

```python
from Crypto.Hash import HMAC, SHA1


key = b'1234'
message = b'Python'
hmac = HMAC.new(key, msg=message, digestmod=SHA1)

```

Сравнить два HMAC можно с помощью методов `verify()` (параметром является HMAC в двоичном виде) и `hexverify()` (параметром является HMAC в шестнадцатеричном виде). В случае, если коды не совпадают, метод выбросит ошибку `ValueError`.

```python
try:
    hmac.hexverify(mac)
    print('Ok')
except ValueError:
    print('Error')

```

Как мы уже знаем, симметричный ключ нужно каким-то образом передать или сгенерировать его с помощью протокола Диффи-Хеллмана. А можно ли использовать RSA? Можно. Для этого стоит рассмотреть **электронно-цифровую подпись** (**ЭЦП**).

Использование ЭЦП такое же, как и MAC: отправитель подписывает (создаёт подпись) сообщения, отправляет её получателю, тот проверяет её и на основе проверки определяет, было ли сообщение изменено и тот ли пользователь отправил это сообщение.

Весь процесс выглядит следующим образом:
1. Отправитель создаёт пару асимметричных ключей.
2. Вычисляет хэш-сумму сообщения.
3. С помощью закрытого ключа шифрует хэш-сумму, получая тем образом подпись.
4. Получатель с помощью открытого ключа отправителя расшифровывает подпись.
5. Хэширует сообщение и проверяет полученный хэш-код с переданным от отправителя.

Очевидно, что если хэши равны, то сообщение не было изменено. Но как проверить, что отправитель не является нарушителем? Для этого мы должны быть уверены в том, что открытый ключ принадлежит именно абоненту A. Для этого используется инфраструктура открытых ключей [**PKI**](https://ru.wikipedia.org/wiki/Инфраструктура_открытых_ключей). PKI – достаточно сложная система, поэтому рассмотрим её поверхностно. Суть состоит в том, что в PKI хранятся **сертификаты** – особого вида документы, в которых имеется информация об открытом ключе и о владельце ключа. PKI гарантирует достоверность сертификатов.

Передача ключей через PKI упрощённо выглядит следующим образом: один пользователь генерирует пару асимметричных ключей и отправляет запрос PKI на создание сертификата с этим ключом, другой пользователь запрашивает у PKI сертификат необходимого пользователя и получает его.
