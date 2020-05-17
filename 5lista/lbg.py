import sys
import collections
import math
from collections import defaultdict

class Pixel:
    def __init__(self, red, green, blue):
        self.r = red
        self.g = green
        self.b = blue

    def __sub__(self, p):
        return Pixel(self.r - p.r, self.g - p.g, self.b - p.b)

    def __add__(self, p):
        return Pixel(self.r + p.r, self.g + p.g, self.b + p.b)

    def __mul__(self, a):
        return Pixel(self.r * a, self.g * a, self.b * a)

    def __truediv__(self, p):
        def is_number(s):
            try:
                float(s)
            except ValueError:
                return False

            return True
        if is_number(p):
            return Pixel(self.r / p, self.g / p, self.b / p)
        else:
            return Pixel(self.r / p.r, self.g / p.g, self.b / p.b)

    def __mod__(self, value):
        return Pixel(self.r % value, self.g % value, self.b % value)

    def floor(self):
        return Pixel(math.floor(self.r), math.floor(self.g), math.floor(self.b))


def avg_vector(pixels):
    avg_vec = Pixel(0, 0, 0)
    for p in pixels:
        if p != None:
            avg_vec += p
    return avg_vec / len(pixels)
    

def avg_distance_to_vec(vec, pixels):
    s = 0
    for v in pixels:
        s += get_distance(vec, v)
    return s / len(pixels)


def avg_distance_list(pixels, l):
    s = 0
    for a, b in zip(pixels, l):
        if a != None and b != None:
            s += get_distance(a, b)
    return s / len(pixels)


def get_distance(a, b):
    return (a.r - b.r) ** 2 + (a.g - b.g) ** 2 + (a.b - b.b) ** 2


def quantify(pixels, codebook):
    bitmap = []
    for p in pixels:
        d = [get_distance(p, c) for c in codebook]
        min_d = min(d)
        bitmap.append(codebook[d.index(min_d)])
    return bitmap


def get_codebook(pixels, size, eps=0.0001):
    codebook = []
    first_vec = avg_vector(pixels)
    codebook.append(first_vec)
    avg_distance = avg_distance_to_vec(first_vec, pixels)
    while len(codebook) < size:
        codebook, avg_distance = get_new_codebook(pixels, codebook, eps, avg_distance)

    return codebook


def get_new_codebook(pixels, codebook, eps, avg_distance):
    new_codebook = []
    for vec in codebook:
        new_codebook.append(vec * (1.0 + eps))
        new_codebook.append(vec * (1.0 - eps))
    codebook = new_codebook

    print('Doubling codebook:', len(codebook))

    new_avg_dist, err = 0, eps + 1.0
    while eps < err:
        neighbour_vec_dict = defaultdict(list)
        neighbour_vec_indexes_dict = defaultdict(list)
        closest_vec_list = [None] * len(pixels)
        for i_p, p in enumerate(pixels):
            min_distance = math.inf
            closest_vec_index = -1
            for i_v, v in enumerate(codebook):
                distance = get_distance(p, v)
                if distance < min_distance:
                    min_distance = distance
                    closest_vec_list[i_p] = v
                    closest_vec_index = i_v
            neighbour_vec_dict[closest_vec_index].append(p)
            neighbour_vec_indexes_dict[closest_vec_index].append(i_p)

        for i_v in range(len(codebook)):
            vectors = neighbour_vec_dict.get(i_v) or []
            if len(vectors) > 0:
                new_vec = avg_vector(vectors)
                for i in neighbour_vec_indexes_dict[i_v]:
                    closest_vec_list[i] = new_vec
                codebook[i_v] = new_vec

        curr_distance = new_avg_dist if new_avg_dist > 0 else avg_distance
        new_avg_dist = avg_distance_list(closest_vec_list, pixels)

        err = (curr_distance - new_avg_dist) / curr_distance

    return codebook, new_avg_dist


def mse(original, b):
    return sum([get_distance(pa, pb) for pa, pb in zip(original, b)]) / len(original)


def snr(bitmap, mse):
    s = 0
    for x in bitmap:
        s += x.r ** 2 + x.g ** 2 + x.b ** 2
    return (s / len(bitmap)) / mse


def encode(content, k):
    imageBytes = content[18:-26]
    pixels = [Pixel(int(imageBytes[i + 2]), int(imageBytes[i + 1]), int(imageBytes[i])) for i in range(0,len(imageBytes),3)]

    result = get_codebook(pixels, 2**k)
    quantified = quantify(pixels, [c.floor() for c in result])
    pixels_array = []
    for p in quantified:
        pixels_array += [p.b, p.g, p.r]
    
    mserror = mse(pixels, quantified)
    snr_value = snr(pixels, mserror)
    print(f'MSE: {mserror}')
    print(f'SNR: {snr_value} ({10 * math.log10(snr_value)} dB)')
    
    return content[:18] + bytes(pixels_array) + content[-26:]


if len(sys.argv) < 4:
    print('Wrong parameters')
    print('python3 lbg.py [input file] [output file] number_of_colors')
    sys.exit(2)

filename = sys.argv[1]
outfilename = sys.argv[2]
k = int(sys.argv[3])
infile = open(filename, mode='rb')
fileContent = infile.read()

res = encode(fileContent, k)

outfile = open(outfilename, mode='wb')
outfile.write(res)

