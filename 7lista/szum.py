import sys
import random


def noise(content, p):
    binstring = ''.join(['{0:08b}'.format(int(x)) for x in content])
    result = ''.join([('1' if c == '0' else '0') if random.random() < p else c for c in binstring])
    return bytes(int(result[i : i + 8], 2) for i in range(0, len(result), 8))


p = float(sys.argv[1])
infilename = sys.argv[2]
outfilename = sys.argv[3]

infile = open(infilename, mode='rb')
result = noise(infile.read(), p)
outfile = open(outfilename, mode='wb')
outfile.write(result)
