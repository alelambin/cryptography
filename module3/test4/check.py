import json
import subprocess
import re
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad


BLOCK_SIZE = 16
PLAINTEXT = b'Python'
KEY = b'A1B2C3D4E5F6G7H8'
IV = b'0000000000000000'

filename = R'~\.result'


def get_encrypt_answer():
    cipher = AES.new(KEY, AES.MODE_CBC, IV)
    return cipher.encrypt(pad(PLAINTEXT, BLOCK_SIZE))


def check_answers(answers):
    if len(answers) != 2:
        return False
    
    if answers[0] == str(get_encrypt_answer()) and answers[1] == PLAINTEXT.decode('utf-8'):
        return True
    else:
        return False


def tweak_line_numbers(error):
    new_error = ''
    for line in error.splitlines():
        match = re.match("(.*, line )([0-9]+)", line)
        if match:
            line = match.group(1) + str(int(match.group(2)))
        new_error += line + '\n'
    return new_error


student_code = """{{ STUDENT_ANSWER | e('py') }}"""

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

if not failed:
    with open(filename, 'r') as file:
        failed = not check_answers(file.read().split('\n')[:-1])
        if failed:
            html += f"<p>Wrong answer</p>"

print(json.dumps({
    'epiloguehtml': html,
    'fraction': 0.0 if failed else 1.0
}))
