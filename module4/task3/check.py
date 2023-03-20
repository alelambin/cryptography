import json
import subprocess
import re
from Crypto.Random import random


SYMBOLS = [chr(num) for num in range(ord(' '), ord('~') + 1) if chr(num) != '\'' and chr(num) != '\\']


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
    PRIMES = [11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, \
        89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173, \
        179, 181, 191, 193, 197, 199, 211, 223, 227, 229, 233, 239, 241, 251, 257, 263, \
        269, 271, 277, 281, 283, 293, 307, 311, 313, 317, 331, 337, 347, 349, 353, 359, \
        367, 373, 379, 383, 389, 397, 401, 409, 419, 421, 431, 433, 439, 443, 449, 457, \
        461, 463, 467, 479, 487, 491, 499, 503, 509, 521, 523, 541, 547, 557, 563, 569, \
        571, 577, 587, 593, 599, 601, 607, 613, 617, 619, 631, 641, 643, 647, 653, 659, \
        661, 673, 677, 683, 691, 701, 709, 719, 727, 733, 739, 743, 751, 757, 761, 769, \
        773, 787, 797, 809, 811, 821, 823, 827, 829, 839, 853, 857, 859, 863, 877, 881, \
        883, 887, 907, 911, 919, 929, 937, 941, 947, 953, 967, 971, 977, 983, 991, 997]
    while True:
        p = random.choice(PRIMES)
        q = random.choice(PRIMES)
        n = p * q
        phi = (p - 1) * (q - 1)
        e = n // 2
        while e < n:
            if gcd(e, phi)[0] == 1:
                break
            e += 1
            if e == n:
                e = 1
        d = 0
        while d == 0:
            t = gcd(e, phi)
            if (t[0] == 1):
                d = t[1] % phi
        yield(''.join([random.choice(SYMBOLS) for _ in range(100)]), e, d, n)


generator = generate_testdata()
TESTDATA = [
    ('TEST', 15, 47, 391),
    ('', 15, 47, 391),
    ('ANOTHER_TEST', 15, 47, 391),
    ('TEST', 1, 1, 391),
    generator.__next__(),
    (''.join(SYMBOLS), 15, 47, 391),
]

filename = R'~\.result'
encrypt_function_name = 'encrypt'
decrypt_function_name = 'decrypt'

PREFIX = """
import json as __json__
"""
POSTFIX = "result = []\n" + ''.join([f"""
ciphertext = {encrypt_function_name}('{DATA[0]}', {DATA[1]}, {DATA[3]})
plaintext = {decrypt_function_name}(ciphertext, {DATA[2]}, {DATA[3]})
result.append({"{'plaintext': plaintext, 'ciphertext': ciphertext}"})
""" for DATA in TESTDATA]) + """
print(__json__.dumps(result))
"""

        
def check_answer(answer, data):
    if len(answer['plaintext']) != len(data[0]) or len(answer['ciphertext']) != len(data[0]):
        return False
    
    result = True
    for i in range(len(data[0])):
        result = result \
            and data[0][i] == answer['plaintext'][i] \
            and ord(data[0][i]) ** data[1] % data[3] == answer['ciphertext'][i]
    return result


def check_answers(answers):
    if len(TESTDATA) != len(answers):
        return False
    
    result = True
    for i in range(len(TESTDATA)):
        result = result and check_answer(answers[i], TESTDATA[i])
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
    failed = True

html = ''
if output:
    html += f"<pre>{output}</pre>"

if re.search("Crypto", student_answer):
    failed = True
    html = "<p>Don't use PyCryptodome module</p>"

if not failed:
    with open(filename, 'r') as file:
        failed = not check_answers(json.loads(file.read()))
        if failed:
            html += f"<p>Wrong answer</p>"

print(json.dumps({
    'epiloguehtml': html,
    'fraction': 0.0 if failed else 1.0
}))
