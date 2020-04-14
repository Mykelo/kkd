import sys
import itertools
import collections
import math

if len(sys.argv) != 2:
    print("Zla liczba argumentow")
    sys.exit(2)

def log(num):
    return math.log2(num) if num > 0 else 0

def entropy(frequencies, fileContent):
    l = len(fileContent)
    return sum([ frequencies[c] * (log(l) - log(frequencies[c])) for c in frequencies]) / l

def conditionalEntropy(frequencies, condFreq, fileContent):
    sumElements = [ condFreq[(y, x)] * (-(log(condFreq[(y, x)]) - log(frequencies[x]))) for y in frequencies for x in frequencies ]
    return sum(sumElements) / len(fileContent)

filename = sys.argv[1]

regularFreq = collections.defaultdict(int)
conditionalFreq = collections.defaultdict(int)
counter = 0
with open(filename, mode='rb') as file:
    fileContent = file.read()
    for i, char in enumerate(fileContent):
        regularFreq[char] += 1        
        if i > 0:
            conditionalFreq[(char, fileContent[i - 1])] += 1
        else:
            conditionalFreq[(char, 0)] = 1

print(filename)
print('Entropy:', entropy(regularFreq, fileContent))
print('Conditional entropy:', conditionalEntropy(regularFreq, conditionalFreq, fileContent))