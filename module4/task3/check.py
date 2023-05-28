import json
import subprocess
import re
import random


SYMBOLS = [chr(num) for num in range(ord(' '), ord('~') + 1) if chr(num) not in ['\'', '\\']]


def gcd(a, b):
    r = (a, b)
    x = (1, 0)
    y = (0, 1)
    q = 0
    while r[1] > 0:
        t = r
        r = (t[1], t[0] % t[1])
        q = t[0] // t[1]
        x = (x[1], x[0] - q * x[1])
        y = (y[1], y[0] - q * y[1])
    return (r[0], x[0], y[0])


def generate_testdata():
    PRIMES = [17, 19, 23, 29, 31, 37, 41, 43, 47, 53, \
              59, 61, 67, 71, 73, 79, 83, 89, 97, 101]
    while True:
        p = random.choice(PRIMES)
        q = random.choice(PRIMES)
        n = p * q
        phi = (p - 1) * (q - 1)
        e = 257
        d = 0
        while d == 0:
            t = gcd(e, phi)
            if (t[0] == 1):
                d = t[1] % phi
        yield(''.join(random.choices(SYMBOLS, k=100)), e, d, n)


generator = generate_testdata()
TESTDATA = [
    ('TEST', 15, 47, 391),
    ('', 15, 47, 391),
    ('ANOTHER_TEST', 15, 47, 391),
    ('TEST', 1, 1, 391),
    generator.__next__(),
    generator.__next__(),
    generator.__next__(),
    (''.join(SYMBOLS), 15, 47, 391),
]
ANSWERS = {
    0: {'user_answer': [None, None], 'correct_answer': [[67, 69, 178, 67], 'TEST']},
    1: {'user_answer': [None, None], 'correct_answer': [[], '']},
    3: {'user_answer': [None, None], 'correct_answer': [[84, 69, 83, 84], 'TEST']}
}

encrypt_filename = R'~\.encrypt_result'
decrypt_filename = R'~\.decrypt_result'
encrypt_function_name = 'encrypt'
decrypt_function_name = 'decrypt'

PREFIX = ""
POSTFIX = f"""
def list_to_string(array, sep=','):
    string = ''
    for element in array:
        string += str(element) + sep
    return string[:-1]

    
TESTDATA = {TESTDATA}

with open('{encrypt_filename}', 'w') as encrypt_file, open('{decrypt_filename}', 'w') as decrypt_file:
    for DATA in TESTDATA:
        ciphertext = {encrypt_function_name}(DATA[0], DATA[1], DATA[3])
        if type(ciphertext) == list:
            encrypt_file.write(list_to_string(ciphertext))
            encrypt_file.write('\\n')
        plaintext = {decrypt_function_name}(ciphertext, DATA[2], DATA[3])
        if type(plaintext) == str:
            decrypt_file.write(plaintext)
            decrypt_file.write('\\n')
"""


def get_student_encrypt_answers(file_string, sep=','):
    array = file_string.split('\n')[:-1]
    res = []
    for string in array:
        res.append(list(map(lambda elem: int(elem), string.split(sep) if len(string) > 0 else [])))
    return res


def get_student_decrypt_answers(file_string):
    return file_string.split('\n')[:-1]


def check_encrypt_answer(answer, data):
    if len(answer) != len(data[0]):
        return False
    
    result = True
    for i in range(len(data[0])):
        result = result and ord(data[0][i]) ** data[1] % data[3] == answer[i]
    return result


def check_decrypt_answer(answer, data):
    if len(answer) != len(data[0]):
        return False
    return data[0] == answer


def check_encrypt_answers(answers):
    if len(TESTDATA) != len(answers):
        return 0
    
    result = 0
    for i in range(len(TESTDATA)):
        if i in ANSWERS:
            ANSWERS[i]['user_answer'][0] = answers[i]
        result += 1 if check_encrypt_answer(answers[i], TESTDATA[i]) else 0
    return result


def check_decrypt_answers(answers):
    if len(TESTDATA) != len(answers):
        return 0
    
    result = 0
    for i in range(len(TESTDATA)):
        if i in ANSWERS:
            ANSWERS[i]['user_answer'][1] = '\'' + answers[i] + '\''
        result += 1 if check_decrypt_answer(answers[i], TESTDATA[i]) else 0
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
    failed = True

html = ''
if output:
    html += f"<pre>{output}</pre>"

if re.search("Crypto", student_answer):
    failed = True
    html = "<p>Don't use PyCryptodome module</p>"

right_answers = 0
if not failed:
    with open(encrypt_filename, 'r') as encrypt_file, open(decrypt_filename, 'r') as decrypt_file:
        right_answers = min(check_encrypt_answers(get_student_encrypt_answers(encrypt_file.read())),\
                            check_decrypt_answers(get_student_decrypt_answers(decrypt_file.read())))
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
            <code style='color:black;'>{encrypt_function_name}('{TESTDATA[i][0]}', {TESTDATA[i][1]}, {TESTDATA[i][3]})</code>
            <br>
            <code style='color:black;'>{decrypt_function_name}({ANSWERS[i]['correct_answer'][0]}, {TESTDATA[i][2]}, {TESTDATA[i][3]})</code>
        </td>
        <td>
            <code style='color:black;'>{ANSWERS[i]['correct_answer'][0]}</code>
            <br>
            <code style='color:black;'>'{ANSWERS[i]['correct_answer'][1]}'</code>
        </td>
        <td>
            <code style='color:black;'>{ANSWERS[i]['user_answer'][0]}</code>
            <br>
            <code style='color:black;'>{ANSWERS[i]['user_answer'][1]}</code>
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
