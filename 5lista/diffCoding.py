import sys
import collections
import math


class Pixel:
    def __init__(self, red, green, blue):
        self.r = red
        self.g = green
        self.b = blue

    def __sub__(self, p):
        return Pixel(self.r - p.r, self.g - p.g, self.b - p.b)

    def __add__(self, p):
        return Pixel(self.r + p.r, self.g + p.g, self.b + p.b)

    def __truediv__(self, p):
        def is_number(s):
            try:
                float(s)
            except ValueError:
                return False

            return True
        if is_number(p):
            return Pixel(self.r // p, self.g // p, self.b // p)
        else:
            return Pixel(self.r // p.r, self.g // p.g, self.b // p.b)

    def __mod__(self, value):
        return Pixel(self.r % value, self.g % value, self.b % value)

    def quantization(self, step):
        self.r = int(self.r // step * step)
        self.g = int(self.g // step * step)
        self.b = int(self.b // step * step)


class PixelsContainer:
    def __init__(self, imageBytes):
        self.pixels = [Pixel(int(imageBytes[i + 2]), int(imageBytes[i + 1]), int(imageBytes[i])) for i in range(0,len(imageBytes),3)]

    def __getitem__(self, pos):
        return self.pixels[pos]


class Stats:
    def __init__(self, pixels):
        code = []
        red = []
        green = []
        blue = []

        for x in range(len(pixels)):
            for y in range(len(pixels[0])):
                p = pixels[x][y]
                code += [p.r, p.g, p.b]
                red.append(p.r)
                green.append(p.g)
                blue.append(p.b)

        self.codeEntropy = self.entropy(code)
        self.redEntropy = self.entropy(red)
        self.greenEntropy = self.entropy(green)
        self.blueEntropy = self.entropy(blue)

    def countFreq(self, content):
        freq = collections.defaultdict(int)
        for c in content:
            freq[c] += 1
        return freq

    def entropy(self, content):
        def log(num):
            return math.log2(num) if num > 0 else 0
        l = len(content)
        freq = self.countFreq(content)
        return sum([freq[c] * (-(log(freq[c]) - log(l))) for c in freq]) / l

    def print(self, text):
        print(text)
        print(f'   code entropy: {self.codeEntropy}')
        print(f'   red entropy: {self.redEntropy}')
        print(f'   green entropy: {self.greenEntropy}')
        print(f'   blue entropy: {self.blueEntropy}')
        print()


def encode(content, k):
    imageBytes = content[18:-26]
    pixels = PixelsContainer(imageBytes)
    print(len(pixels.pixels))

    lastPixel = None
    step = 256 / (2 ** k)
    result = []
    for p in pixels.pixels:
        if lastPixel == None:
            lastPixel = p
            result.append(p)
        else:
            d = p - lastPixel
            d.quantization(step)


if len(sys.argv) < 2:
    print('File name missing')
    sys.exit(2)

filename = sys.argv[1]
infile = open(filename, mode='rb')
fileContent = infile.read()

encode(fileContent, 7)
