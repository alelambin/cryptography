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
ANSWERS = {
    0: {'user_answer': [None, None], 'correct_answer': [None, None]},
    1: {'user_answer': [None, None], 'correct_answer': [None, None]},
    8: {'user_answer': [None, None], 'correct_answer': [None, None]}
}

encrypt_filename = R'~\.encrypt_result'
decrypt_filename = R'~\.decrypt_result'
encrypt_function_name = 'encrypt'
decrypt_function_name = 'decrypt'

PREFIX = """
from math import log2 as __log2__
"""
POSTFIX = f"""
def write_bytes(file, barray):
    for byte in barray:
        file.write(('' if byte > 15 else '0') + hex(byte)[2:])
    file.write('\\n')


with open('{encrypt_filename}', 'w') as encrypt_file, open('{decrypt_filename}', 'w') as decrypt_file:
    """ + '\n'.join(list(map(lambda DATA: f"""
    ciphertext = {encrypt_function_name}('{DATA[0]}', {DATA[1]}, {DATA[2]})
    plaintext = {decrypt_function_name}(ciphertext, {DATA[1]}, {DATA[2]})
    if type(ciphertext) == bytes:
        write_bytes(encrypt_file, ciphertext)
    if type(plaintext) == str:
        decrypt_file.write(plaintext + '\\n')
""", TESTDATA)))


def get_encrypt_student_answers(file_string):
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


def get_decrypt_student_answers(char_string):
    return char_string.split('\n')[:-1]


def get_answer(data):
    return AES.new(data[1], AES.MODE_CBC, data[2]).encrypt(pad(data[0].encode('utf-8'), BLOCK_SIZE))


def check_answers(encrypt_answers, decrypt_answers):
    if len(TESTDATA) != len(encrypt_answers) or len(TESTDATA) != len(decrypt_answers):
        return 0
    
    result = 0
    for i in range(len(TESTDATA)):
        correct_answer = [get_answer(TESTDATA[i]), TESTDATA[i][0]]
        user_answer = [encrypt_answers[i], decrypt_answers[i]]
        if i in ANSWERS:
            ANSWERS[i]['user_answer'] = user_answer
        result += 1 if correct_answer[0] == user_answer[0] and correct_answer[1] == user_answer[1] else 0
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
student_answer = """
{{ STUDENT_ANSWER | e('py') }}
"""
student_code += student_answer
student_code += POSTFIX
for i in ANSWERS:
    ANSWERS[i]['correct_answer'] = [get_answer(TESTDATA[i]), TESTDATA[i][0]]

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

right_answers = 0
if not failed:
    with open(encrypt_filename, 'r') as encrypt_file, open(decrypt_filename, 'r') as decrypt_file:
        right_answers = check_answers(get_encrypt_student_answers(encrypt_file.read()), get_decrypt_student_answers(decrypt_file.read()))
        failed = right_answers < len(TESTDATA)

html += f"""<div>
<table border>
    <thead>
        <tr>
            <th scope="col">
                <div>
                    <div>Входные данные</div>
                </div>
            </th>
            <th scope="col">Правильное решение</th>
            <th scope="col">Ваше решение</th>
        </tr>
    </thead>
    <tbody>
""" + '\n'.join([f"""
    <tr>
        <td>
            <code style='color:black;'>{encrypt_function_name}('{TESTDATA[i][0]}', {TESTDATA[i][1]}, {TESTDATA[i][1]})</code>
            <br>
            <code style='color:black;'>{decrypt_function_name}({ANSWERS[i]['correct_answer'][0]}, {TESTDATA[i][1]}, {TESTDATA[i][1]})</code>
        </td>
        <td>
            <code style='color:black;'>{ANSWERS[i]['correct_answer'][0]}</code>
            <br>
            <code style='color:black;'>'{ANSWERS[i]['correct_answer'][1]}'</code>
        </td>
        <td>
            <code style='color:black;'>{ANSWERS[i]['user_answer'][0]}</code>
            <br>
            <code style='color:black;'>'{ANSWERS[i]['user_answer'][1]}'</code>
        </td>
    </tr>
""" for i in ANSWERS]) + """
    </tbody>
</table>
</div>
<br>
"""
html += f"<p>Пройдено тестов: {right_answers}<br>Всего тестов: {len(TESTDATA)}</p>"

print(json.dumps({
    'epiloguehtml': html,
    'fraction': 0.0 if failed else 1.0
}))
