import sys

class Tree:
    def __init__(self):
        self.elements = []
        self.seen = {}
    
    def addElements(self, elements):
        self.elements = elements
        self.seen = {}
        for i, x in enumerate(elements):
            self.seen[x[0]] = i

    def add(self, symbol):
        if symbol in self.seen:
            index = self.seen[symbol]
            self.elements[index][1] += 1
            
            for i in range(index - 1, -1, -1):
                if self.elements[i][1] >= self.elements[index][1]:
                    self.seen[symbol] = i + 1
                    self.seen[self.elements[i + 1][0]] = index
                    self.elements[i + 1][2], self.elements[index][2] = self.elements[index][2], self.elements[i + 1][2]
                    self.elements[i + 1], self.elements[index] = self.elements[index], self.elements[i + 1]
                    self.updateTree(i + 1)
                    break
                elif i == 0:
                    self.seen[symbol] = 0
                    self.seen[self.elements[0][0]] = index
                    self.elements[0][2], self.elements[index][2] = self.elements[index][2], self.elements[0][2]
                    self.elements[0], self.elements[index] = self.elements[index], self.elements[0]
        else:
            index = len(self.elements)
            self.seen[symbol] = index
            self.elements.append([symbol, 1, 0])
            self.updateTree(index)

    def updateTree(self, index):
        index += 1
        while index > 1:
            index, remainder = divmod(index, 2)
            if remainder == 0:
                # left child
                self.elements[index - 1][2] += 1

    def getSumFreq(self, symbol):
        if symbol not in self.seen:
            return 0, 1
        index = self.seen[symbol]
        indexFromOne = index + 1
        af = 0
        while indexFromOne > 1:
            indexFromOne, remainder = divmod(indexFromOne, 2)
            if remainder == 1:
                # right child
                el = self.elements[indexFromOne - 1]
                af += el[1] + el[2]
        return af, self.elements[index][1]

    def countFreq(self):
        return sum([x[1] for x in self.elements])


def encode(fileContent):
    low = 0
    high = 1
    lowInt = 0
    highInt = 10 ** 14
    tree = Tree()
    tree.add(fileContent[0])
    size = 1
    for char in fileContent[1:]:
        charLow, count = tree.getSumFreq(char)
        # print("Char low:", charLow, "| count:", count)
        charHigh = charLow + count
        print(chr(char), charLow, size, charLow / size, charHigh / size)
        newLow = low + (high - low) * (charLow / size)
        newHigh = low + (high - low) * (charHigh / size)
        low, high = newLow, newHigh
        lowInt = int(highInt * low)
        highInt = int(highInt * high)
        tree.add(char)
        size += 1

    return lowInt, highInt - 1, tree.elements

def decode(code, characters):
    tree = Tree()
    tree.addElements(characters)
    totalFreq = tree.countFreq()
    decoded = ""
    low = 0
    high = 10 ** 24
    while totalFreq > 0:
        index = int(((code - low + 1) * totalFreq - 1) / (high - low + 1))




# t = Tree()
# while True:
#     x = input()
#     t.add(x)
#     print(t.elements, t.seen)
filename = sys.argv[1]

with open(filename, mode='rb') as file:
    fileContent = file.read()
    print(encode(fileContent))
