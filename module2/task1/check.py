import json
import subprocess
import re
import random


ALPHABET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

TESTDATA = [
    ('TEST', 3),
    ('TEST', 0),
    ('', 1),
    ('TEST', 26),
    ('TEST', 100),
    ('TEST', -3),
    ('TEST', -100),
    (''.join(random.choices(ALPHABET, k=1000)), random.randint(1, 25)),
    (''.join(random.choices(ALPHABET, k=1000)), random.randint(-25, 1)),
]
ANSWERS = {
    0: {'user_answer': None, 'correct_answer': 'WHVW'},
    1: {'user_answer': None, 'correct_answer': 'TEST'},
    2: {'user_answer': None, 'correct_answer': ''}
}

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
    
    result = 0
    for i in range(len(TESTDATA)):
        correct_answer = get_answer(TESTDATA[i])
        user_answer = answers[i]
        if i in ANSWERS:
            ANSWERS[i]['user_answer'] = user_answer
        result += 1 if correct_answer == user_answer else 0
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
student_code += """
{{ STUDENT_ANSWER | e('py') }}
"""
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
    
right_answers = 0
if not failed:
    with open(filename, 'r') as file:
        right_answers = check_answers(file.read().split('\n')[:-1])
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
        <td><code style='color:black;'>encrypt('{TESTDATA[i][0]}', {TESTDATA[i][1]})</code></td>
        <td><code style='color:black;'>'{ANSWERS[i]['correct_answer']}'</code></td>
        <td><code style='color:black;'>'{ANSWERS[i]['user_answer']}'</code></td>
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
