import sys


def check(content1, content2):
    binstring1 = ''.join(['{0:08b}'.format(int(x)) for x in content1])
    binstring2 = ''.join(['{0:08b}'.format(int(x)) for x in content2])
    print(binstring1)
    print(binstring2)
    if len(binstring1) != len(binstring2):
        raise ValueError('Different length of files')
        
    diffs = [i for i in range(0, len(binstring1), 4) if binstring1[i:i+4] != binstring2[i:i+4]]
    return len(diffs)


in1 = sys.argv[1]
in2 = sys.argv[2]

file1 = open(in1, mode='rb')
file2 = open(in2, mode='rb')

try:
    diffs = check(file1.read(), file2.read())
    print(f'Rozne bloki: {diffs}')
except ValueError as err:
    print(err)
    sys.exit(2)