import sys
import collections
import math


class Pixel:
    def __init__(self, red, green, blue):
        self.r = red
        self.g = green
        self.b = blue

    def __sub__(self, p):
        return Pixel((self.r - p.r) % 256, (self.g - p.g) % 256, (self.b - p.b) % 256)

    def __add__(self, p):
        return Pixel((self.r + p.r) % 256, (self.g + p.g) % 256, (self.b + p.b) % 256)

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


class PixelsContainer:
    def __init__(self, imageBytes, width, height):
        pixels = []
        for i in range(height):
            col = []
            for j in range(width):
                index = (i * width + j) * 3
                p = Pixel(int(imageBytes[index + 2]), int(
                    imageBytes[index + 1]), int(imageBytes[index]))
                col.append(p)
            pixels.append(col)
        self.pixels = list(reversed(pixels))
        self.width = width
        self.height = height

    def __getitem__(self, pos):
        x, y = pos
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return Pixel(0, 0, 0)
        return self.pixels[y][x]


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


def scheme1(pixels, x, y):
    w = pixels[x - 1, y]
    return Pixel(w.r, w.g, w.b)


def scheme2(pixels, x, y):
    n = pixels[x, y - 1]
    return Pixel(n.r, n.g, n.b)


def scheme3(pixels, x, y):
    nw = pixels[x - 1, y - 1]
    return Pixel(nw.r, nw.g, nw.b)


def scheme4(pixels, x, y):
    w = pixels[x - 1, y]
    nw = pixels[x - 1, y - 1]
    n = pixels[x, y - 1]
    return n + w - nw


def scheme5(pixels, x, y):
    w = pixels[x - 1, y]
    nw = pixels[x - 1, y - 1]
    n = pixels[x, y - 1]
    return n + (w - nw) / 2


def scheme6(pixels, x, y):
    w = pixels[x - 1, y]
    nw = pixels[x - 1, y - 1]
    n = pixels[x, y - 1]
    return w + (n - nw) / 2


def scheme7(pixels, x, y):
    w = pixels[x - 1, y]
    n = pixels[x, y - 1]
    return (n + w) / 2


def scheme8(pixels, x, y):
    w = pixels[x - 1, y]
    nw = pixels[x - 1, y - 1]
    n = pixels[x, y - 1]

    def byColor(wc, nwc, nc):
        if nwc > max(wc, nc):
            return max(wc, nc)
        if nwc < min(wc, nc):
            return min(wc, nc)
        return (wc + nc - nwc) % 256

    return Pixel(
        byColor(w.r, nw.r, n.r),
        byColor(w.g, nw.g, n.g),
        byColor(w.b, nw.b, n.b)
    )


def JPEG(pixels, scheme):
    diffPixels = []
    for i in range(pixels.width):
        col = []
        for j in range(pixels.height):
            x = pixels[i, j]
            xdash = scheme(pixels, i, j)
            col.append(x - xdash)
        diffPixels.append(col)

    return diffPixels


def countEntropies(content):
    width = int(content[13]) << 8 | (int(content[12]))
    height = int(content[15]) << 8 | (int(content[14]))
    imageBytes = content[18:-26]
    pixels = PixelsContainer(imageBytes, width, height)
    fileEntropy = Stats(pixels.pixels)

    schemes = [
        [scheme1, 'W'],
        [scheme2, 'N'],
        [scheme3, 'NW'],
        [scheme4, 'N + W - NW'],
        [scheme5, 'N + (W - NW) / 2'],
        [scheme6, 'W + (N - NW) / 2'],
        [scheme7, '(N + W) / 2'],
        [scheme8, 'new standard'],
    ]

    fileEntropy.print('Input file:')
    for scheme in schemes:
        s = Stats(JPEG(pixels, scheme[0]))
        scheme.append(s)
        s.print(f'For {scheme[1]}')

    bestForCode = min(schemes, key=lambda x: x[2].codeEntropy)
    bestForRed = min(schemes, key=lambda x: x[2].redEntropy)
    bestForGreen = min(schemes, key=lambda x: x[2].greenEntropy)
    bestForBlue = min(schemes, key=lambda x: x[2].blueEntropy)

    print('Best')
    print(f'for code ({bestForCode[1]}): {bestForCode[2].codeEntropy}')
    print(f'for red ({bestForRed[1]}): {bestForRed[2].redEntropy}')
    print(f'for green ({bestForGreen[1]}): {bestForGreen[2].greenEntropy}')
    print(f'for blue ({bestForBlue[1]}): {bestForBlue[2].blueEntropy}')


filename = sys.argv[1]
infile = open(filename, mode='rb')
fileContent = infile.read()

countEntropies(fileContent)
