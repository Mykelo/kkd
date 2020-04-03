import sys

class Node:
    def __init__(self, code, weight):
        self.code = code
        self.left = None
        self.right = None
        self.parent = None
        self.weight = weight

class Tree:
    def __init__(self):
        self.seen = { 'NYT': Node('NYT', 0) }
        self.root = self.seen['NYT']
        self.currPos = self.root

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

    def updateTree(self, node):
        n = node
        while n != None:
            n.weight += 1
            if n.parent != None and n.parent.right != n and n.parent.right.weight < n.weight:
                n.parent.right, n.parent.left = n.parent.left, n.parent.right
            n = n.parent

    def addChar(self, char):
        if char not in self.seen:
            nyt = self.seen['NYT']
            nytCode = self.getCode(nyt)
            parentNode = Node('', 1)
            codeNode = Node(char, 1)
            parentNode.parent = nyt.parent
            parentNode.left = nyt
            parentNode.right = codeNode
            nyt.parent = parentNode
            codeNode.parent = parentNode
            self.seen[char] = codeNode
            self.updateTree(parentNode.parent)

            # Make sure the root is updated
            if parentNode.parent == None:
                self.root = parentNode
            else:
                parentNode.parent.left = parentNode
            return nytCode, False
        else:
            n = self.seen[char]
            code = self.getCode(n)
            self.updateTree(n)
            return code, True

    def inOrder(self, node, level):
        if node == None:
            return
        
        self.inOrder(node.left, level + 1)
        print('  ' * level, '[', node.code, node.weight, ']')
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
        decoded = ""
        tree = Tree()
        # Read first e bits
        value = content[0:8]
        char = str(chr(self.invertedCodes[value]))
        decoded += char
        tree.addChar(char)
        tree.resetPath()
        content = content[8:]

        while content != "":
            char = content[0]
            content = content[1:]
            code = tree.goNext(char)
            if code == "NYT":
                nextEBits = content[0:self.e]
                decodedChar = str(chr(self.invertedCodes[nextEBits]))
                decoded += decodedChar
                tree.addChar(decodedChar)
                content = content[self.e:]
                tree.resetPath()
            elif code != "":
                decoded += code
                tree.addChar(code)
                tree.resetPath()

        return decoded


coder = Coder()
arg = sys.argv[1]
filename = sys.argv[2]
outfilename = sys.argv[3]

if arg == "--encode":
    infile = open(filename, mode='rb')
    fileContent = infile.read()
    encoded = coder.encode(fileContent)
    print(encoded)
    b = bytes(int(encoded[i : i + 8], 2) for i in range(0, len(encoded), 8))

    outfile = open(outfilename, mode='wb')
    outfile.write(b)
elif arg == "--decode":
    outfile = open(filename, mode='rb')
    fileContent = outfile.read()
    hexstring = fileContent.hex()
    binstring = ''.join(["{0:08b}".format(int(hexstring[x:x + 2], base=16)) for x in range(0, len(hexstring), 2)])
    decoded = coder.decode(binstring)
    print(decoded)
    outfile = open(outfilename, mode='w')
    outfile.write(decoded)