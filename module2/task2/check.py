import json
import subprocess
import re
import random


ALPHABET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

TESTDATA = [
    ('Test', 3),
    ('Test', 0),
    ('', 1),
    ('Test', 26),
    ('Test', 100),
    ('Test', -3),
    ('Test', -100),
    (''.join(random.choices(ALPHABET, k=1000)), random.randint(1, 25)),
    (''.join(random.choices(ALPHABET, k=1000)), random.randint(-25, 1)),
]

PREFIX = []
POSTFIX = [f"print(encrypt('{DATA[0]}', {DATA[1]}))" for DATA in TESTDATA]
filename = R'~\.result.txt'


def get_answer(data):
    answer = ''
    for letter in data[0]:
        answer += ALPHABET[(ord(letter) - 65 + data[1]) % len(ALPHABET)]
    return answer


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
            line = match.group(1) + str(int(match.group(2)) - len(PREFIX) - 1)
        new_error += line + '\n'
    return new_error


student_code = '\n'.join(PREFIX) + '\n'
student_code += """{{ STUDENT_ANSWER | e('py') }}"""
student_code += '\n'.join(POSTFIX) + '\n'

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
except subprocess.CalledProcessError as e:
    outcome = e
    output = "Task failed with return code = {}\n".format(outcome.returncode)
    failed = True
except subprocess.TimeoutExpired as e:
    outcome = e
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
            html += f"<pre>Wrong answer</pre>"

print(json.dumps({
    'epiloguehtml': html,
    'fraction': 0.0 if failed else 1.0
}))
