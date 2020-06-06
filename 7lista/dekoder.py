import sys
import numpy as np

# Parity check matrix
H = np.array([
    [1, 0, 1, 0, 1, 0, 1, 0],
    [0, 1, 1, 0, 0, 1, 1, 0],
    [0, 0, 0, 1, 1, 1, 1, 0],
    [1, 1, 1, 1, 1, 1, 1, 1]
])

# Decoding matrix
D = np.array([
    [0, 0, 1, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 1, 0, 0, 0],
    [0, 0, 0, 0, 0, 1, 0, 0],
    [0, 0, 0, 0, 0, 0, 1, 0]
])


def correct(code, syndrome):
    hamming_syndrome = syndrome[:3]
    parity = syndrome[3]

    # No errors
    if parity == 0 and sum(hamming_syndrome) == 0:
        return code

    # Error at the end   
    if parity == 1 and sum(hamming_syndrome) == 0:
        code[-1] = (code[-1] + 1) % 2
        return code

    # One error
    if parity == 1:
        position = sum(hamming_syndrome * [1, 2, 4]) - 1
        code[position] = (code[position] + 1) % 2
        return code

    raise ValueError('Double error')

def decode(content):
    binstring = ''.join(['{0:08b}'.format(int(x)) for x in content])
    result = ''
    double_errors = 0
    for i in range(0, len(binstring), 8):
        code = binstring[i:i+8]
        a = np.array([int(c) for c in code])
        x = np.dot(H, a)
        x %= 2
        corrected = a
        try:
            corrected = correct(a, x)
        except:
            double_errors += 1

        decoded = np.dot(D, corrected.T)
        decoded %= 2
        result += ''.join(map(str, map(int, decoded)))

    return result, double_errors

infilename = sys.argv[1]
outfilename = sys.argv[2]

infile = open(infilename, mode='rb')
decoded, double_errors = decode(infile.read())
print(f'Podwojne bledy: {double_errors}')
outfile = open(outfilename, mode='wb')
outfile.write(bytes(int(decoded[i : i + 8], 2) for i in range(0, len(decoded), 8)))
