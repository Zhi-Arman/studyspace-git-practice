"""Original classroom code, transcribed without changing its behavior."""


def f(l, t):
    r = []
    for x in l:
        if x[2] == t:
            if x[3] > 0:
                r.append(x[0] + " " + x[1])
    return r


def g(l, t):
    r = []
    for x in l:
        if x[2] == t:
            if x[4] > 0:
                r.append(x[0] + " " + x[1])
    return r
