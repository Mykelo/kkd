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
    return output

def decode(content, dictSize, decoder):
    content = decoder.decode(content)
    size = 256
    dictionary = {i: str(chr(i)) for i in range(256)}
    output = []
    I = str(chr(content[0]))
    output.append(I)
    for x in content[1:]:
        if x in dictionary:
            J = dictionary[x]
        elif x == size:
            J = I + I[0]
        else:
            raise ValueError("Wrong compression")
        output.append(J)

        if size < dictSize:
            dictionary[size] = I + J[0]
            size += 1
            I = J
        else:
            size = 256
            dictionary = {i: str(chr(i)) for i in range(256)}
            I = str(chr(x))
    return "".join(output)

def countFreq(content):
    freq = collections.defaultdict(int)
    for c in content:
        freq[c] += 1
    return freq

def entropy(content, valuesSet, freq):
    def log(num):
        return math.log2(num) if num > 0 else 0
    l = len(content)
    return sum([ freq[c] * (-(log(freq[c]) - log(l))) for c in valuesSet]) / l

def countStats(file, code, codeBytes):
    fileFreq = countFreq(file)
    codeFreq = countFreq(code)
    compressionRate = len(file) / len(codeBytes)
    fileEntropy = entropy(file, range(256), fileFreq)
    codeEntropy = entropy(file, codeFreq, codeFreq)

    return len(file), len(codeBytes), compressionRate, fileEntropy, codeEntropy

arg = sys.argv[1]
filename = sys.argv[2]
outfilename = sys.argv[3]
coder = EliasDeltaCode()

fileLen = 0
encodedLen = 0
compressionRate = 0
textEntropy = 0
codeEntropy = 0

if arg == "--encode":
    infile = open(filename, mode='rb')
    fileContent = infile.read()
    encoded = encode(fileContent, 2**16)
    s = ''.join([coder.encode(x) for x in encoded])
    b = bytes(int(s[i : i + 8], 2) for i in range(0, len(s), 8))

    fileLen, encodedLen, compressionRate, textEntropy, codeEntropy = countStats(fileContent, encoded, b)
    print(f'File length: {fileLen}')
    print(f'Code length: {encodedLen}')
    print(f'Compression rate: {compressionRate}')
    print(f'File entropy: {textEntropy}')
    print(f'Code entropy: {codeEntropy}')

    outfile = open(outfilename, mode='wb')
    outfile.write(b)
elif arg == "--decode":
    outfile = open(filename, mode='rb')
    fileContent = outfile.read()
    hexstring = fileContent.hex()
    binstring = ''.join(["{0:08b}".format(int(hexstring[x:x + 2], base=16)) for x in range(0, len(hexstring), 2)])
    decoded = decode(binstring, 2**16, coder)
    outfile = open(outfilename, mode='wb')
    outfile.write(bytes(decoded, 'UTF-8'))

print(ord("ą"))