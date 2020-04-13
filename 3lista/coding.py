
class EliasOmegaCode:
    def encode(self, n):
        code = '0'
        while n > 1:
            binary = '{0:b}'.format(n)
            code = binary + code
            n = len(binary) - 1

        return code

    def decode(self, code):
        numbers = []
        n = 1
        i = 0
        while i < len(code):
            if code[i] == '0':
                numbers.append(n)
                n = 1
                i += 1
            elif code[i] == '1':
                s = code[i:i + n + 1]
                i += n + 1
                n = int(s, 2)
        return numbers


class EliasGammaCode:
    def encode(self, n):
        code = '{0:b}'.format(n)
        return '0' * (len(code) - 1) + code

    def decode(self, code):
        numbers = []
        N = 0
        i = 0
        while i < len(code):
            if code[i] == '0':
                N += 1
                i += 1
            else:
                numbers.append(int(code[i:i + N + 1], 2))
                i += N + 1
                N = 0

        return numbers


class EliasDeltaCode:
    def __init__(self):
        self.gamma = EliasGammaCode()

    def encode(self, x):
        binary = '{0:b}'.format(x)
        n = self.gamma.encode(len(binary))
        return n + binary[1:]

    def decode(self, code):
        numbers = []
        L = 0
        i = 0
        while i < len(code):
            if code[i] == '0':
                L += 1
                i += 1
            else:
                N = int(code[i:i + L + 1], 2) - 1
                i += L + 1
                numbers.append(int('1' + code[i:i + N], 2))
                i += N
                L = 0

        return numbers


class FibonacciCode:
    def fib(self, n, isListLen=False):
        l = []
        a, b = 0, 1
        if not isListLen:
            while a <= n:
                l.append(a)
                a, b = b, a + b
        else:
            for _ in range(n + 2):
                l.append(a)
                a, b = b, a + b
        return l[2:]

    def encode(self, n):
        seq = self.fib(n)
        binary = ['0' for _ in seq]
        while n > 0:
            i, x = [(i, x) for i, x in enumerate(seq) if x <= n][-1]
            binary[i] = '1'
            n = n % x
        binary.append('1')
        return ''.join(binary)

    def decode(self, code):
        separateCodes = [x + '1' for x in code.split('11')][0:-1]
        seq = self.fib(max([len(x) for x in separateCodes]), True)
        return [sum([seq[i] if x == '1' else 0 for i, x in enumerate(code)]) for code in separateCodes]

