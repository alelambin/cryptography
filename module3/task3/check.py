import json
import subprocess
import re
from Crypto.Cipher import DES
from Crypto.Random import get_random_bytes


BLOCK_SIZE = 8

TESTDATA = [
    (b'12345678', b'-KEYKEY-', bytes(BLOCK_SIZE)),
    (b'12345678', b'-KEYKEY-', b'12345678'),
    (b'1234567812345678', b'-KEYKEY-', bytes(BLOCK_SIZE)),
    (b'1234567890', b'-KEYKEY-', bytes(BLOCK_SIZE)),
    (b'1234567890', b'*KEYKEY*', bytes(BLOCK_SIZE)),
    (b'', b'-KEYKEY-', bytes(BLOCK_SIZE)),
    (get_random_bytes(1000), get_random_bytes(BLOCK_SIZE), get_random_bytes(BLOCK_SIZE)),
]

filename = R'~\.result'
function_name = 'encrypt_CBC'
byteorder = 'big'
delimiter = b'\x00'

PREFIX = """
from math import log2 as __log2__
from Crypto.Cipher import DES as __DES__


def encrypt_block(plain_block, key):
    if len(plain_block) != 8:
        raise ValueError('invalid plain_block size')
    if len(key) != 8:
        raise ValueError('invalid key size')
    
    cipher = __DES__.new(key, __DES__.MODE_ECB)
    return cipher.encrypt(plain_block)

"""
POSTFIX = f"""
with open('{filename}', 'wb') as file:
    """ + '\n'.join(list(map(lambda DATA: f"""
    ciphertext = {function_name}({DATA[0]}, {DATA[1]}, {DATA[2]})
    length = len(ciphertext)
    length_byte_size = 1 + int(__log2__(length)) // 8 if length > 0 else 1
    file.write(length.to_bytes(length_byte_size, '{byteorder}') + {delimiter} + ciphertext)
""", TESTDATA)))


def get_student_answers(byte_string):
    array = []
    index = 0
    while index < len(byte_string):
        delimiter_index = byte_string.find(delimiter, index + 1)
        length = int.from_bytes(byte_string[index:delimiter_index], 'big')
        answer_index = delimiter_index + 1
        index = answer_index + length
        array.append(byte_string[answer_index:index])
    return array


def get_answer(data):
    block_index = 0
    length = len(data[0])
    cipher = DES.new(data[1], DES.MODE_ECB)
    ciphertext = b''
    prev_block = data[2]
    while block_index < length:
        block = data[0][block_index : block_index + BLOCK_SIZE] \
            if block_index + BLOCK_SIZE <= length \
            else data[0][block_index : length] + bytes([0] * (BLOCK_SIZE - (length - block_index)))
        new_block = cipher.encrypt(bytes([_1 ^ _2 for _1, _2 in zip(prev_block, block)]))
        ciphertext += new_block
        prev_block = new_block 
        block_index += BLOCK_SIZE
    return ciphertext


def check_answers(answers):
    if len(TESTDATA) != len(answers):
        return False
    
    result = True
    for i in range(len(TESTDATA)):
        result = result and (get_answer(TESTDATA[i]) == answers[i])
    return result


def tweak_line_numbers(error):
    new_error = ''
    for line in error.splitlines():
        match = re.match("(.*, line )([0-9]+)", line)
        if match:
            line = match.group(1) + str(int(match.group(2)) - PREFIX.count('\n') - 1)
        new_error += line + '\n'
    return new_error


student_code = PREFIX + '\n'
student_answer = """{{ STUDENT_ANSWER | e('py') }}"""
student_code += student_answer
student_code += POSTFIX

output = ''
failed = False
try:
    outcome = subprocess.run(
        ['python3', '-c', student_code],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=2,
        universal_newlines=True,
        check=True
    )
except subprocess.CalledProcessError as error:
    outcome = error
    output = "Task failed with return code = {}\n".format(outcome.returncode)
    failed = True
except subprocess.TimeoutExpired as error:
    outcome = error
    output = "Task timed out\n"
if outcome.stderr:
    output += "*** Error output ***\n"
    output += tweak_line_numbers(outcome.stderr)

html = ''
if output:
    html += f"<pre>{output}</pre>"

if re.search("Crypto", student_answer) or re.search("__DES__", student_answer):
    failed = True
    html = "<p>Don't use PyCryptodome module</p>"

if not failed:
    with open(filename, 'rb') as file:
        failed = not check_answers(get_student_answers(file.read()))
        if failed:
            html += f"<p>Wrong answer</p>"

print(json.dumps({
    'epiloguehtml': html,
    'fraction': 0.0 if failed else 1.0
}))
