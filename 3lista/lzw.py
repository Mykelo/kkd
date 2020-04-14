import sys
from coding import EliasOmegaCode, EliasGammaCode, EliasDeltaCode, FibonacciCode
import os
import collections
import math


def encode(content, dictSize):
    size = 256
    dictionary = {str(chr(i)): i for i in range(256)}
    output = []
    I = str(chr(content[0]))
    for x in content[1:]:
        J = str(chr(x))
        if I + J in dictionary:
            I = I + J
        else:
            output.append(dictionary[I])
            if size < dictSize:
                dictionary[I + J] = size
                size += 1
                I = J
            else:
                size = 256
                dictionary = {str(chr(i)): i for i in range(256)}
                I = str(chr(x))
    if I:
        output.append(dictionary[I])

    print(len(output))
    return output

def decode(content, dictSize, decoder):
    content = decoder.decode(content)
    print(len(content))
    size = 256
    dictionary = {i: [i] for i in range(256)}
    output = []
    I = [content[0]]
    output.append(I)
    for x in content[1:]:
        if x in dictionary:
            J = dictionary[x]
        elif x == size:
            J = I + [I[0]]
        else:
            raise ValueError("Wrong compression")
        output.append(J)

        if size < dictSize:
            dictionary[size] = I + [J[0]]
            size += 1
            I = J
        else:
            size = 256
            dictionary = {i: [i] for i in range(256)}
            I = [x]
    output = bytes([item for subl in output for item in subl])
    return output.decode('utf-8')

def countFreq(content):
    freq = collections.defaultdict(int)
    for c in content:
        freq[c] += 1
    return freq

def entropy(content, freq):
    def log(num):
        return math.log2(num) if num > 0 else 0
    l = len(content)
    return sum([ freq[c] * (-(log(freq[c]) - log(l))) for c in freq]) / l

def countStats(file, code, codeBytes):
    fileFreq = countFreq(file)
    codeFreq = countFreq(code)
    compressionRate = len(file) / len(codeBytes)
    fileEntropy = entropy(file, fileFreq)
    codeEntropy = entropy(file, codeFreq)

    return len(file), len(codeBytes), compressionRate, fileEntropy, codeEntropy

def handleArgs(argv):
    if len(argv) < 4:
        raise ValueError('Wrong number of arguments')

    def index(a_list, value):
        try:
            return a_list.index(value)
        except ValueError:
            return None
    size = 2**16
    coder = EliasOmegaCode()
    action = argv[1]
    filename = argv[2]
    outfilename = argv[3]

    if action not in ['--encode', '--decode']:
        raise ValueError(f'Wrong action argument: {action}')

    i = index(argv, '--size')
    if i:
        if i + 1 < len(argv) and argv[i + 1].isdigit() and int(argv[i + 1]) >= 512:
            size = int(argv[i + 1])
        else:
            raise ValueError('Wrong argument: --size')
    
    if '--delta' in argv:
        coder = EliasDeltaCode()
    elif '--gamma' in argv:
        coder = EliasGammaCode()
    elif '--fib' in argv:
        coder = FibonacciCode()

    return action, filename, outfilename, coder, size

try:
    action, filename, outfilename, coder, size = handleArgs(sys.argv)
except ValueError as error:
    print(error)
    sys.exit(2)

fileLen = 0
encodedLen = 0
compressionRate = 0
textEntropy = 0
codeEntropy = 0

if action == "--encode":
    infile = open(filename, mode='rb')
    fileContent = infile.read()
    encoded = encode(fileContent, size)
    s = ''.join([coder.encode(x) for x in encoded])
    b = bytes(int(s[i : i + 8], 2) for i in range(0, len(s), 8))
    # decode(encoded, size, coder)
    # print(encoded)
    # print(coder.decode(s))
    
    fileLen, encodedLen, compressionRate, textEntropy, codeEntropy = countStats(fileContent, encoded, b)
    print(f'File length: {fileLen}')
    print(f'Code length: {encodedLen}')
    print(f'Compression rate: {compressionRate}')
    print(f'File entropy: {textEntropy}')
    print(f'Code entropy: {codeEntropy}')

    outfile = open(outfilename, mode='wb')
    outfile.write(b)
    outfile.close()


    testfile = open(outfilename, mode='rb')
    fileContent = testfile.read()
    hexstring = fileContent.hex()
    binstring = ''.join(["{0:08b}".format(int(hexstring[x:x + 2], base=16)) for x in range(0, len(hexstring), 2)])
    # print(b)
    # print(hexstring)
    print(all(i == j for i, j in zip(encoded, coder.decode(binstring))) )
    print(binstring == s)
    print(len(binstring), len(s))
elif action == "--decode":
    outfile = open(filename, mode='rb')
    fileContent = outfile.read()
    hexstring = fileContent.hex()
    binstring = ''.join(["{0:08b}".format(int(hexstring[x:x + 2], base=16)) for x in range(0, len(hexstring), 2)])
    decoded = decode(binstring, size, coder)
    outfile = open(outfilename, mode='wb')
    outfile.write(bytes(decoded, 'UTF-8'))
