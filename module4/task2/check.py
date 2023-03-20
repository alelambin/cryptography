import json
import subprocess
import re
from Crypto.Random import random


def build_number(pairs):
    number = 1
    for (base, power) in pairs:
        number *= base ** power
    return number


def generate_testdata():
    PRIME = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101]
    MAX_POWER = 10
    while True:
        sample_base = random.sample(PRIME, len(PRIME))
        index = random.randint(0, len(PRIME) - 1)
        sample_base = (sample_base[:index], sample_base[index:])
        yield (
            build_number(zip(sample_base[0], [random.randint(0, MAX_POWER) for _ in range(len(sample_base[0]))])),
            build_number(zip(sample_base[1], [random.randint(0, MAX_POWER) for _ in range(len(sample_base[1]))]))
        )

generator = generate_testdata()
TESTDATA = [
    (64, 81),
    (81, 64),
    (2, 6),
    (0, 7),
    generator.__next__(),
    generator.__next__(),
    generator.__next__(),
    (random.randint(2, 10 ** 5), random.randint(2, 10 ** 5)),
    (random.randint(2, 10 ** 5), random.randint(2, 10 ** 10)),
    (random.randint(2, 10 ** 10), random.randint(2, 10 ** 10)),
]

filename = R'~\.result'
function_name = 'modular_multiplicative_inverse'

PREFIX = ''
POSTFIX = '\n' + '\n'.join([f'print({function_name}({DATA[0]}, {DATA[1]}))' for DATA in TESTDATA])


def gcd(a, b):
    while b != 0:
        (a, b) = (b, a % b)
    return a


def get_student_answers(char_string):
    return char_string.split('\n')[:-1]


def check_answers(answers):
    if len(TESTDATA) != len(answers):
        return False
    
    result = True
    for i in range(len(TESTDATA)):
        number = TESTDATA[i][0]
        module = TESTDATA[i][1]
        result = result \
            and answers[i].isnumeric() \
            and (gcd(number, module) != 1 and number * int(answers[i]) % module == 0 \
            or number * int(answers[i]) % module == 1)
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
student_code += """{{ STUDENT_ANSWER | e('py') }}"""
student_code += POSTFIX

output = ''
failed = False
try:
    with open(filename, 'w')as file:
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
        failed = not check_answers(get_student_answers(file.read()))
        if failed:
            html += f"<p>Wrong answer</p>"

print(json.dumps({
    'epiloguehtml': html,
    'fraction': 0.0 if failed else 1.0
}))
