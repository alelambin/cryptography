import json
import subprocess
import re
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes


filename_public_key_1024 = R'~\public1024.pem'
filename_private_key_1024 = R'~\private1024.pem'
filename_public_key_2048 = R'~\public2048.pem'
filename_private_key_2048 = R'~\private2048.pem'
TESTDATA = [
    (b'12345678', filename_public_key_1024, filename_private_key_1024),
    (b'12345678', filename_public_key_2048, filename_private_key_2048),
    (b'12345678ABCDEFGH', filename_public_key_1024, filename_private_key_1024),
    (b'1234567890', filename_public_key_1024, filename_private_key_1024),
    (b'', filename_public_key_1024, filename_private_key_1024),
    (get_random_bytes(16), filename_public_key_1024, filename_private_key_1024),
]

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
    ciphertext = {encrypt_function_name}({DATA[0]}, '{DATA[1]}')
    plaintext = {decrypt_function_name}(ciphertext, '{DATA[2]}')
    if type(ciphertext) == bytes:
        write_bytes(encrypt_file, ciphertext)
    if type(plaintext) == bytes:
        write_bytes(decrypt_file, plaintext)
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


def get_answer(byte_string, filename):
    with open(filename, 'rb') as file:
        key = RSA.import_key(file.read())
    return PKCS1_OAEP.new(key).decrypt(byte_string)


def check_answers(encrypt_answers, decrypt_answers):
    if len(TESTDATA) != len(encrypt_answers) or len(TESTDATA) != len(decrypt_answers):
        return 0

    result = 0
    for i in range(len(TESTDATA)):
        try:
            result += 1 if (TESTDATA[i][0] == get_answer(encrypt_answers[i], TESTDATA[i][2])) \
                and (TESTDATA[i][0] == decrypt_answers[i]) else 0
        except:
            pass
    return result


def tweak_line_numbers(error):
    new_error = ''
    for line in error.splitlines():
        match = re.match("(.*, line )([0-9]+)", line)
        if match:
            line = match.group(1) + str(int(match.group(2)) - PREFIX.count('\n') - 1)
        new_error += line + '\n'
    return new_error


with open(filename_public_key_1024, 'wb') as public_key_file, open(filename_private_key_1024, 'wb') as private_key_file:
    key = RSA.generate(1024)
    private_key_file.write(key.export_key())
    public_key_file.write(key.public_key().export_key())
with open(filename_public_key_2048, 'wb') as public_key_file, open(filename_private_key_2048, 'wb') as private_key_file:
    key = RSA.generate(2048)
    private_key_file.write(key.export_key())
    public_key_file.write(key.public_key().export_key())

student_code = PREFIX + '\n'
student_code += """
{{ STUDENT_ANSWER | e('py') }}
"""
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

right_answers = 0
if not failed:
    with open(encrypt_filename, 'r') as encrypt_file, open(decrypt_filename, 'r') as decrypt_file:
        right_answers = check_answers(get_student_answers(encrypt_file.read()), get_student_answers(decrypt_file.read()))
        failed = right_answers < len(TESTDATA)

html += f"<p>Пройдено тестов: {right_answers}<br>Всего тестов: {len(TESTDATA)}</p>"

print(json.dumps({
    'epiloguehtml': html,
    'fraction': 0.0 if failed else 1.0
}))
