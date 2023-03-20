def modular_multiplicative_inverse(e, m):
    r = (e, m)
    d = (1, 0)
    q = 0
    while r[1] > 0:
        t = r
        r = (t[1], t[0] % t[1])
        q = t[0] // t[1]
        d = (d[1], d[0] - q * d[1])
    if r[0] == 1:
        return d[0] % m
    else:
        return 0
