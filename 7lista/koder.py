import sys
import numpy as np

G = np.array([
    [1, 1, 1, 0, 0, 0, 0, 1],
    [1, 0, 0, 1, 1, 0, 0, 1],
    [0, 1, 0, 1, 0, 1, 0, 1],
    [1, 1, 0, 1, 0, 0, 1, 0]
])


def encode(content):
    binstring = ''.join(['{0:08b}'.format(int(x)) for x in content])
    result = ''
    for i in range(0, len(binstring), 4):
        a = np.array([int(c) for c in binstring[i:i+4]])
        x = np.dot(a, G)
        x %= 2
        result += ''.join(map(str, map(int, x)))
    return result

infilename = sys.argv[1]
outfilename = sys.argv[2]

infile = open(infilename, mode='rb')
content = infile.read()
encoded = encode(content)
outfile = open(outfilename, mode='wb')
outfile.write(bytes(int(encoded[i : i + 8], 2) for i in range(0, len(encoded), 8)))
