import json
import subprocess
import re
from Crypto.Cipher import DES
from Crypto.Random import get_random_bytes


BLOCK_SIZE = 8

TESTDATA = [
    (b'12345678', b'-KEYKEY-'),
    (b'1234567812345678', b'-KEYKEY-'),
    (b'1234567890', b'-KEYKEY-'),
    (b'1234567890', b'*KEYKEY*'),
    (b'', b'-KEYKEY-'),
    (get_random_bytes(1000), get_random_bytes(BLOCK_SIZE)),
]

filename = R'~\.result'
function_name = 'encrypt_ECB'

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
def write_bytes(file, barray):
    for byte in barray:
        file.write(('' if byte > 15 else '0') + hex(byte)[2:])
    file.write('\\n')


with open('{filename}', 'w') as file:
    """ + '\n'.join(list(map(lambda DATA: f"""
    ciphertext = {function_name}({DATA[0]}, {DATA[1]})
    write_bytes(file, ciphertext)
""", TESTDATA)))


def get_student_answers(file_string):
    answers = file_string.split('\n')[:-1]
    result = []
    for answer in answers:
        byte_array = b''
        index = 0
        while index < len(answer):
            byte_array += int(answer[index:(index + 2)], 16).to_bytes(1, 'big')
            index += 2
        result.append(byte_array)
    return result


def get_answer(data):
    block_index = 0
    length = len(data[0])
    cipher = DES.new(data[1], DES.MODE_ECB)
    ciphertext = b''
    while block_index < length:
        block = data[0][block_index : block_index + BLOCK_SIZE] \
            if block_index + BLOCK_SIZE <= length \
            else data[0][block_index : length] + bytes([0] * (BLOCK_SIZE - (length - block_index)))
        ciphertext += cipher.encrypt(block)
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
    with open(filename, 'r') as file:
        failed = not check_answers(get_student_answers(file.read()))
        if failed:
            html += f"<p>Wrong answer</p>"

print(json.dumps({
    'epiloguehtml': html,
    'fraction': 0.0 if failed else 1.0
}))
