import json
import subprocess
import re
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Random.random import choice
from Crypto.Util.Padding import pad


BLOCK_SIZE = 16

SYMBOLS = [chr(num) for num in range(ord(' '), ord('~') + 1) if chr(num) != '\'' and chr(num) != '\\']
TESTDATA = [
    ('ABCDEFGHIJKLMNOP', b'-16B-SECRET-KEY-', bytes(BLOCK_SIZE)),
    ('ABCDEFGHIJKLMNOP', b'-----24B-SECRET-KEY-----', bytes(BLOCK_SIZE)),
    ('ABCDEFGHIJKLMNOP', b'-32B-SECRET-KEY--32B-SECRET-KEY-', bytes(BLOCK_SIZE)),
    ('ABCDEFGHIJKLMNOP', b'-16B-SECRET-KEY-', get_random_bytes(BLOCK_SIZE)),
    ('12345678ABCDEFGHIJKLMNOP12345678', b'-16B-SECRET-KEY-', bytes(BLOCK_SIZE)),
    ('ABCDEFGHIJKLMNOPQRSTUVWXYZ', b'-16B-SECRET-KEY-', bytes(BLOCK_SIZE)),
    ('ABCDEFGHIJKLMNOPQRSTUVWXYZ', b'-16B-SECRET-KEY-', get_random_bytes(BLOCK_SIZE)),
    ('ABCDEFGHIJKLMNOPQRSTUVWXYZ', b'*16B*SECRET*KEY*', bytes(BLOCK_SIZE)),
    ('', b'-16B-SECRET-KEY-', bytes(BLOCK_SIZE)),
    (''.join([choice(SYMBOLS) for _ in range(1000)]), get_random_bytes(BLOCK_SIZE), get_random_bytes(BLOCK_SIZE)),
]

encrypt_filename = R'~\.encrypt_result'
decrypt_filename = R'~\.decrypt_result'
encrypt_function_name = 'encrypt'
decrypt_function_name = 'decrypt'
byteorder = 'big'
delimiter = b'\x00'

PREFIX = """
from math import log2 as __log2__
"""
POSTFIX = f"""
with open('{encrypt_filename}', 'wb') as encrypt_file, open('{decrypt_filename}', 'w') as decrypt_file:
    """ + '\n'.join(list(map(lambda DATA: f"""
    ciphertext = {encrypt_function_name}('{DATA[0]}', {DATA[1]}, {DATA[2]})
    plaintext = {decrypt_function_name}(ciphertext, {DATA[1]}, {DATA[2]})
    length = len(ciphertext)
    length_byte_size = 1 + int(__log2__(length)) // 8 if length > 0 else 1
    encrypt_file.write(length.to_bytes(length_byte_size, '{byteorder}') + {delimiter} + ciphertext)
    decrypt_file.write(plaintext + '\\n')
""", TESTDATA)))


def get_encrypt_student_answers(byte_string):
    array = []
    index = 0
    while index < len(byte_string):
        delimiter_index = byte_string.find(delimiter, index + 1)
        length = int.from_bytes(byte_string[index:delimiter_index], 'big')
        answer_index = delimiter_index + 1
        index = answer_index + length
        array.append(byte_string[answer_index:index])
    return array


def get_decrypt_student_answers(char_string):
    return char_string.split('\n')[:-1]


def get_answer(data):
    return AES.new(data[1], AES.MODE_CBC, data[2]).encrypt(pad(data[0].encode('utf-8'), BLOCK_SIZE))


def check_answers(encrypt_answers, decrypt_answers):
    if len(TESTDATA) != len(encrypt_answers) or len(TESTDATA) != len(decrypt_answers):
        return False
    
    result = True
    for i in range(len(TESTDATA)):
        if get_answer(TESTDATA[i]) != encrypt_answers[i] or TESTDATA[i][0] != decrypt_answers[i]:
            print(get_answer(TESTDATA[i]), encrypt_answers[i])
            print(TESTDATA[i][0], decrypt_answers[i])
        result = result and (get_answer(TESTDATA[i]) == encrypt_answers[i]) and (TESTDATA[i][0] == decrypt_answers[i])
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

if not failed:
    with open(encrypt_filename, 'rb') as encrypt_file, open(decrypt_filename, 'r') as decrypt_file:
        failed = not check_answers(get_encrypt_student_answers(encrypt_file.read()), get_decrypt_student_answers(decrypt_file.read()))
        if failed:
            html += f"<p>Wrong answer</p>"

print(json.dumps({
    'epiloguehtml': html,
    'fraction': 0.0 if failed else 1.0
}))
