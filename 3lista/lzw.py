import sys
from coding import EliasOmegaCode, EliasGammaCode, EliasDeltaCode, FibonacciCode
import os

def initDict(initSize, dictSize):
    return [{'parent': -1, 'index': c, 'symbol': c} if c < initSize else {'parent': -1, 'index': -1, 'symbol': ''} for c in range(dictSize)]

def findNextEntry(dictionary, pointer, I):
    expectedIndex = pointer
    returnPointer = pointer
    isFull = True
    for _ in range(len(dictionary)):
        pointer = (pointer + 1) % len(dictionary)
        if dictionary[pointer]['parent'] == I and dictionary[pointer]['index'] == expectedIndex:
            isFull = False
            return True, pointer, isFull
        elif dictionary[pointer]['index'] == -1:
            returnPointer = pointer
            isFull = False
    return False, returnPointer, isFull


# def encode(content, dictSize, encoder):
#     if len(content) == 0:
#         return []
#     dictionary = initDict(256, dictSize)
#     output = []
#     x = int(content[0])
#     I = x
#     # output.append(x)

#     def update(pointer, I, J):
#         # print('Printing:', I)
#         dictionary[pointer]['parent'] = I
#         dictionary[pointer]['index'] = pointer
#         dictionary[pointer]['symbol'] = J
#         output.append(I)
#         return J

#     for x in content[1:]:
#         J = x
#         pointer = hash((I, J)) % dictSize
#         print(x, I, pointer, dictionary[pointer])
#         if dictionary[pointer]['index'] == -1:
#             # Entry is unused
#             I = update(pointer, I, J)
#         elif dictionary[pointer]['index'] == pointer and dictionary[pointer]['parent'] == I:
#             # Entry is in the dictionary
#             I = pointer
#         else:
#             used, newPointer, isFull = findNextEntry(
#                 dictionary, pointer, I)
#             if isFull:
#                 print("FULL")
#                 I = x
#                 dictionary = initDict(256, dictSize)
#                 continue
#             # print('Collision', used, newPointer)
#             if used:
#                 I = newPointer
#             else:
#                 I = update(newPointer, I, J)

#     output.append(I)
#     print(len(output))
#     return ''.join([encoder.encode(x) for x in output])

def encode(content, dictSize, encoder):
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
            dictionary[I + J] = size
            size += 1
            I = J
    if I:
        output.append(dictionary[I])
    print(len(output))
    return ''.join([encoder.encode(x) for x in output])

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

        dictionary[size] = I + J[0]
        size += 1

        I = J
    return "".join(output)


# def decode(content, dictSize, decoder):
#     content = decoder.decode(content)
#     if len(content) == 0:
#         return []
#     dictionary = initDict(256, dictSize)
#     output = []
#     x = int(content[0])
#     I = x
#     output.append(x)

#     def findRightNode(pointer):
#         expectedPointer = pointer
#         for _ in range(len(dictionary)):
#             if dictionary[pointer]['index'] == expectedPointer:
#                 return dictionary[pointer]
#             pointer = (pointer + 1) % len(dictionary)

#     def retrieveString(pointer):
#         symbols = []
#         while pointer != -1:
#             print(pointer, dictionary[pointer])
#             node = findRightNode(pointer)
#             symbols.append(pointer)
#             pointer = node['parent']
#         return symbols[::-1]

#     for pointer in content[1:]:
#         J = retrieveString(pointer)
#         output += J
#         x = J[0]

#         loc = hash((I, x)) % dictSize
#         print(pointer, I, J, loc, dictionary[loc])
#         if dictionary[loc]['index'] == loc and dictionary[loc]['parent'] != I:
#             _, newLoc, isFull = findNextEntry(dictionary, loc, I)
#             if isFull:
#                 print("FULL")
#                 I = x
#                 output.append(I)
#                 dictionary = initDict(256, dictSize)
#                 continue
#             loc = newLoc

#         dictionary[loc]['parent'] = I
#         dictionary[loc]['index'] = loc
#         dictionary[loc]['symbol'] = x
#         I = J[-1]
#     return "".join([str(chr(dictionary[x]['symbol'])) for x in output])


# print(encode('', 256))
arg = sys.argv[1]
filename = sys.argv[2]
outfilename = sys.argv[3]
coder = EliasDeltaCode()

# file = open(filename, mode='rb')
# content = file.read()
# encoded = encode(content, 2**16, coder)
# print(encoded)
# decoded = decode(encoded, 2**16, coder)
# print(decoded)


if arg == "--encode":
    infile = open(filename, mode='rb')
    fileContent = infile.read()
    encoded = encode(fileContent, 2**9, coder)
    print(len(encoded))
    print(f'size of file: {os.path.getsize(filename)} b')
    b = bytes(int(encoded[i : i + 8], 2) for i in range(0, len(encoded), 8))

    outfile = open(outfilename, mode='wb')
    outfile.write(b)
elif arg == "--decode":
    outfile = open(filename, mode='rb')
    fileContent = outfile.read()
    hexstring = fileContent.hex()
    binstring = ''.join(["{0:08b}".format(int(hexstring[x:x + 2], base=16)) for x in range(0, len(hexstring), 2)])
    print(f'size of compressed file: {os.path.getsize(filename)} b')
    decoded = decode(binstring, 2**9, coder)
    print(decoded)
    outfile = open(outfilename, mode='w')
    outfile.write(decoded)