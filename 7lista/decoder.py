import sys
import numpy as np


H = np.array([
    [1, 0, 1, 0, 1, 0, 1, 0],
    [0, 1, 1, 0, 0, 1, 1, 0],
    [0, 0, 0, 1, 1, 1, 1, 0],
    [1, 1, 1, 1, 1, 1, 1, 1]
])

D = np.array([
    [0, 0, 1, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 1, 0, 0, 0],
    [0, 0, 0, 0, 0, 1, 0, 0],
    [0, 0, 0, 0, 0, 0, 1, 0]
])


def correct(code, syndrome):
    code_array = [c for c in code]
    hamming_syndrome = syndrome[:3]
    parity = syndrome[3]
    if parity == 0 and sum(hamming_syndrome) == 0:
        return code
    if parity == 1 and sum(hamming_syndrome) == 0:
        code_array[-1] = '1' if code_array[-1] == '0' else '0'
        return ''.join(code_array)
    if parity == 1:
        position = sum(hamming_syndrome * [1, 2, 4])
        code_array[position-1] = '1' if code_array[position-1] == '0' else '0'
        return ''.join(code_array)

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
        corrected = code
        try:
            corrected = correct(code, x)
        except:
            double_errors += 1
            result += code

        corrected_arr = np.array([int(c) for c in corrected])
        decoded = np.dot(D, corrected_arr.T)
        result += ''.join(map(str, map(int, decoded)))

    return result, double_errors

infilename = sys.argv[1]
outfilename = sys.argv[2]

infile = open(infilename, mode='rb')
decoded, double_errors = decode(infile.read())
print(f'Double errors: {double_errors}')
outfile = open(outfilename, mode='wb')
outfile.write(bytes(int(decoded[i : i + 8], 2) for i in range(0, len(decoded), 8)))
