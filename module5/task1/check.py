import json
import subprocess
import re
from Crypto.Hash import MD5
from Crypto.Random import get_random_bytes


TESTDATA = [
    (b'1234', b'Test'),
    (b'1234', b''),
    (b'12345678', b'Test'),
    (b'1234567890', b'Test'),
    (b'', b'Test'),
    (get_random_bytes(8), get_random_bytes(8)),
    (get_random_bytes(3), get_random_bytes(5)),
]
ANSWERS = {
    0: {'user_answer': None, 'correct_answer': b'\x8b3\xc2\xb9A \xc1#\x19\xa5\xb1Q_>\x03\xed'},
    1: {'user_answer': None, 'correct_answer': b'\x05\xba\x9a\x93\x0b\xc6e`\xbcq3\x8b\x1a\xe3;I'},
    4: {'user_answer': None, 'correct_answer': b'\x9f\xe4\xe8\xae%[\xd2\xd7\xceU"V\xf1z\xfc\xda'}
}

filename = R'~\.result'
function_name = 'nmac'

PREFIX = """
from Crypto.Hash import MD5 as __MD5__


def h(bytestring):
    digest = __MD5__.new(bytestring)
    return digest.digest()

"""
POSTFIX = f"""
def write_bytes(file, barray):
    for byte in barray:
        file.write(('' if byte > 15 else '0') + hex(byte)[2:])
    file.write('\\n')


with open('{filename}', 'w') as file:
    """ + '\n'.join(list(map(lambda DATA: f"""
    result = {function_name}({DATA[0]}, {DATA[1]})
    if type(result) == bytes:
        write_bytes(file, result)
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


def h(bytestring):
    return MD5.new(bytestring).digest()


def get_answer(data):
    return h(data[0] + h(data[0] + data[1]))


def check_answers(answers):
    if len(TESTDATA) != len(answers):
        return 0

    result = 0
    for i in range(len(TESTDATA)):
        if i in ANSWERS:
            ANSWERS[i]['user_answer'] = answers[i]
        result += 1 if get_answer(TESTDATA[i]) == answers[i] else 0
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

if re.search("Crypto", student_answer) or re.search("__MD5__", student_answer):
    failed = True
    html = "<p>Don't use PyCryptodome module</p>"

right_answers = 0
if not failed:
    with open(filename, 'r') as file:
        right_answers = check_answers(get_student_answers(file.read()))
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
        <td><code style='color:black;'>{function_name}({TESTDATA[i][0]}, {TESTDATA[i][1]})</code></td>
        <td><code style='color:black;'>{ANSWERS[i]['correct_answer']}</code></td>
        <td><code style='color:black;'>{ANSWERS[i]['user_answer']}</code></td>
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
