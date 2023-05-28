import json
import subprocess
import re
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA3_512
from Crypto.Random import get_random_bytes


TESTDATA = [
    b'1234',
    b'0000',
    b'ABCDEF',
    b'',
    get_random_bytes(8),
    get_random_bytes(11),
]

filename = R'~\.result'
function_name = 'sign'

PREFIX = """
import json as __json__
from Crypto.PublicKey.RSA import RsaKey as __KeyType__
"""
POSTFIX = f"""
def bytes_to_str(byte_array):
    string = ''
    for byte in byte_array:
        string += ('' if byte > 15 else '0') + hex(byte)[2:]
    return string


result = []
TESTDATA = {TESTDATA}
for DATA in TESTDATA:
    signature, key = {function_name}(DATA)
    if type(signature) == bytes and type(key) == __KeyType__:
        result.append({"{'sign': bytes_to_str(signature), 'key': bytes_to_str(key.export_key())}"})
print(__json__.dumps(result))
"""


def str_to_bytes(string):
    byte_array = b''
    index = 0
    while index < len(string):
        byte_array += int(string[index:(index + 2)], 16).to_bytes(1, 'big')
        index += 2
    return byte_array


def check_answers(answers):
    if len(TESTDATA) != len(answers):
        return 0

    result = 0
    for i in range(len(TESTDATA)):
        try:
            key = RSA.import_key(str_to_bytes(answers[i]['key']))
            signature = str_to_bytes(answers[i]['sign'])
            digest = SHA3_512.new(TESTDATA[i])
            pkcs1_15.new(key).verify(digest, signature)
            result += 1
        except (ValueError, TypeError):
           return False
    return result


def tweak_line_numbers(error):
    new_error = ''
    for line in error.splitlines():
        match = re.match("(.*, line )([0-9]+)", line)
        if match:
            line = match.group(1) + str(int(match.group(2)) - PREFIX.count('\n') - 1)
        new_error += line + '\n'
    return new_error


student_answer = """
{{ STUDENT_ANSWER | e('py') }}
"""
student_code = PREFIX + '\n' + student_answer + POSTFIX

output = ''
failed = False
try:
    with open(filename, 'w') as file:
        outcome = subprocess.run(
            ['python3', '-c', student_code],
            stdout=file,
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
    with open(filename, 'r') as file:
        right_answers = check_answers(json.loads(file.read()))
        failed = right_answers < len(TESTDATA)

html += f"<p>Пройдено тестов: {right_answers}<br>Всего тестов: {len(TESTDATA)}</p>"

print(json.dumps({
    'epiloguehtml': html,
    'fraction': 0.0 if failed else 1.0
}))
