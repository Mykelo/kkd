import sys
import os
import math
import collections

class Node:
    def __init__(self, code, weight, value):
        self.code = code
        self.left = None
        self.right = None
        self.parent = None
        self.weight = weight
        self.value = value
    
    def isLeaf(self):
        return not self.left and not self.right

class Tree:
    def __init__(self):
        self.seen = { 'NYT': Node('NYT', 0, 256) }
        self.root = self.seen['NYT']
        self.nodes = []
        self.indexes = {}
        self.currPos = self.root
        self.currValue = 256

    def goNext(self, char):
        if char == '1':
            self.currPos = self.currPos.right
        else:
            self.currPos = self.currPos.left

        return self.currPos.code

    def getCode(self, node):
        code = ''
        n = node
        while n.parent != None:
            if n.parent.right == n:
                code += '1'
            else:
                code += '0'
            n = n.parent
        return code[::-1]

    def findLargest(self, node):
        # print([f'[{n.code}, {n.weight}, {n.value}] ' for n in self.nodes])
        return next(n for n in reversed(self.nodes) if n.weight == node.weight and node.parent is not n)

    def swap(self, n1, n2):
        i1, i2 = self.nodes.index(n1), self.nodes.index(n2)
        self.nodes[i1], self.nodes[i2] = self.nodes[i2], self.nodes[i1]
        # print(i1, i2)
        # print('swaping:', n1.code, n1.weight, n1.value, 'with', n2.code, n2.weight, n2.value)
        n1.parent, n2.parent = n2.parent, n1.parent
        n1.value, n2.value = n2.value, n1.value

        if n1.parent.left is n2:
            n1.parent.left = n1
        else:
            n1.parent.right = n1

        if n2.parent.left is n1:
            n2.parent.left = n2
        else:
            n2.parent.right = n2

    def updateWeights(self, node):
        if not node:
            return 0
        if node.code == '':
            node.weight = self.updateWeights(node.left) + self.updateWeights(node.right)
        return node.weight

    def updateTree(self, node):
        n = node
        # while n != None:
        #     n.weight += 1
        #     if n.parent != None and n.parent.right != n and n.parent.right.weight < n.weight:
        #         n.parent.right, n.parent.left = n.parent.left, n.parent.right
        #     n = n.parent
        while n:
            largest = self.findLargest(n)

            # self.inOrder(self.root)
            # print('checking:', n.code, n.weight, n.value, 'with', largest.code, largest.weight, largest.value)
            if (n is not largest and node is not largest.parent and
                largest is not n.parent):
                self.swap(n, largest)

            # if n.code != '':
                # print('adding weight')
            n.weight += 1
            n = n.parent
        # self.updateWeights(self.root)

    def addChar(self, char):
        if char not in self.seen:
            nyt = self.seen['NYT']
            nytCode = self.getCode(nyt)
            parentNode = Node('', 1, nyt.value)
            self.currValue -= 1
            codeNode = Node(char, 1, self.currValue)
            self.nodes = [codeNode, parentNode] + self.nodes
            self.currValue -= 1
            nyt.value = self.currValue
            parentNode.parent = nyt.parent
            parentNode.left = nyt
            parentNode.right = codeNode
            nyt.parent = parentNode
            codeNode.parent = parentNode
            self.seen[char] = codeNode

            # Make sure the root is updated
            if parentNode.parent == None:
                self.root = parentNode
            else:
                parentNode.parent.left = parentNode
            self.updateTree(parentNode)
            return nytCode, False
        else:
            n = self.seen[char]
            code = self.getCode(n)
            self.updateTree(n)
            return code, True

    def inOrder(self, node, level=0):
        if node == None:
            return
        
        self.inOrder(node.left, level + 1)
        print('  ' * level, '[', node.code, node.weight, node.value, ']')
        self.inOrder(node.right, level + 1)

    def resetPath(self):
        self.currPos = self.root


class Coder:
    def __init__(self):
        self.fixedCodes = {x: "{0:08b}".format(x-1) for x in range(1, 256)}
        self.invertedCodes = {v: k for k, v in self.fixedCodes.items()}
        self.e = 8
        self.r = 0

    def encode(self, content):
        tree = Tree()
        encoded = ""
        for char in content:
            code, seen = tree.addChar(char)
            if seen:
                encoded += code
            else:
                encoded += code + self.fixedCodes[char]
        return encoded

    def decode(self, content):
        decoded = []
        tree = Tree()
        # Read first e bits
        value = content[0:8]
        char = self.invertedCodes[value]
        decoded.append(char)
        tree.addChar(char)
        tree.resetPath()
        content = content[8:]

        i = 0
        while content != '':
            char = content[0]
            content = content[1:]
            code = tree.goNext(char)
            print(i)
            i += 1
            if code == 'NYT':
                nextEBits = content[0:self.e]
                decodedChar = self.invertedCodes[nextEBits]
                decoded.append(decodedChar)
                tree.addChar(decodedChar)
                content = content[self.e:]
                tree.resetPath()
            elif code != '':
                decoded.append(code)
                tree.addChar(code)
                tree.resetPath()

        return bytes(decoded).decode('utf-8')

def countStats(fileContent, encoded):
    def countFreq(content):
        freq = collections.defaultdict(int)
        for c in content:
            freq[c] += 1
        return freq
    def log(num):
        return math.log2(num) if num > 0 else 0

    frequencies = countFreq(fileContent)
    l = len(fileContent)
    entropy = sum([ frequencies[c] * (log(l) - log(frequencies[c])) for c in frequencies]) / l
    averageCodeLen = len(encoded) / l
    compressionRate = l / math.ceil(len(encoded) / 8)

    return entropy, averageCodeLen, compressionRate
    

coder = Coder()
arg = sys.argv[1]
filename = sys.argv[2]
outfilename = sys.argv[3]

if arg == "--encode":
    infile = open(filename, mode='rb')
    fileContent = infile.read()
    encoded = coder.encode(fileContent)

    entropy, averageCodeLen, compressionRate = countStats(fileContent, encoded)
    print(f'entropy: {entropy}')
    print(f'average length of code: {averageCodeLen}')
    print(f'compression rate: {compressionRate}')

    print(f'size of file: {os.path.getsize(filename)} b')
    b = bytes(int(encoded[i : i + 8], 2) for i in range(0, len(encoded), 8))

    outfile = open(outfilename, mode='wb')
    outfile.write(b)
elif arg == "--decode":
    outfile = open(filename, mode='rb')
    fileContent = outfile.read()
    hexstring = fileContent.hex()
    binstring = ''.join(["{0:08b}".format(int(hexstring[x:x + 2], base=16)) for x in range(0, len(hexstring), 2)])
    print(len(binstring))
    print(f'size of compressed file: {os.path.getsize(filename)} b')
    decoded = coder.decode(binstring)
    print(decoded)
    outfile = open(outfilename, mode='w')
    outfile.write(decoded)