"""
    Helpers lib
"""
import sys

def get_uniques(words):
    v = list(words)
    r = []
    s = set()

    for i in v:
        if i[0] not in s:
            r.append(i)
            s.add(i[0])
    return r

def myprint(string):
    sys.stdout.write(string)
    sys.stdout.flush()


