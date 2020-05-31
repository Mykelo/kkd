import sys
import collections
import math
import os


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
            return Pixel(self.r // p, self.g // p, self.b // p)
        else:
            return Pixel(self.r // p.r, self.g // p.g, self.b // p.b)

    def __mod__(self, value):
        return Pixel(self.r % value, self.g % value, self.b % value)

    def quantization(self, step):
        r = int(self.r // step * step)
        g = int(self.g // step * step)
        b = int(self.b // step * step)
        return Pixel(r, g, b)


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
        ret_x, ret_y = x, y
        if x < 0:
            ret_x = 0
        elif x >= self.width:
            ret_x = self.width - 1
        
        if y < 0:
            ret_y = 0
        elif y >= self.height:
            ret_y = self.height - 1

        return self.pixels[ret_y][ret_x]


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



def filter_pass(pixels, x, y, f):
    s = Pixel(0, 0, 0)
    for i in range(-1, 2):
        for j in range(-1, 2):
            s += pixels[x + i, y + j] * f[i + 1][j + 1]

    weight_sum = sum([sum(row) for row in f])
    if weight_sum <= 0:
        weight_sum = 1

    s /= weight_sum
    if s.r < 0:
        s.r = 0
    if s.g < 0:
        s.g = 0
    if s.b < 0:
        s.b = 0

    if s.r > 255:
        s.r = 255
    if s.g > 255:
        s.g = 255
    if s.b > 255:
        s.b = 255

    return s


def differential_coding(pixels):
    a = pixels[0]
    result = [a]
    for p in pixels[1:]:
        a = p - a
        result.append(a)
        a = p

    return result

def differential_decoding(diffs):
    a = diffs[0]
    result = [a]
    for q in diffs[1:]:
        a = a + q
        result.append(a)

    return result


def quantize(pixels, k):
    step = 256 // (2**k)
    return [p.quantization(step) for p in pixels]


def get_distance(a, b):
    return (a - b) ** 2


def mse(original, b):
    return sum([get_distance(pa, pb) for pa, pb in zip(original, b)]) / len(original)


def snr(bitmap, mse_value):
    return (sum([get_distance(p, 0) for p in bitmap]) / len(bitmap)) / mse_value


def get_stats(original, modified):
    original_extracted = []
    for p in original:
        original_extracted += [p.b, p.g, p.r]

    original_extracted_r = [p.r for p in original]
    original_extracted_g = [p.g for p in original]
    original_extracted_b = [p.b for p in original]

    modified_extracted = []
    for p in modified:
        modified_extracted += [p.b, p.g, p.r]

    modified_extracted_r = [p.r for p in modified]
    modified_extracted_g = [p.g for p in modified]
    modified_extracted_b = [p.b for p in modified]

    mserror = mse(original_extracted, modified_extracted)
    mserror_r = mse(original_extracted_r, modified_extracted_r)
    mserror_g = mse(original_extracted_g, modified_extracted_g)
    mserror_b = mse(original_extracted_b, modified_extracted_b)
    snr_value = snr(original_extracted, mserror)
    return mserror, mserror_r, mserror_g, mserror_b, snr_value


def decode(content):
    width = int(content[13]) << 8 | (int(content[12]))
    height = int(content[15]) << 8 | (int(content[14]))
    imageBytes = content[18:-26]
    hexstring = imageBytes.hex()

    # Read the first 3 bits and calculate how many bits at the end are useless
    binstring = ''.join(["{0:08b}".format(int(hexstring[x:x + 2], base=16)) for x in range(0, len(hexstring), 2)])
    endBits = int(binstring[0:3], 2)
    binstring = binstring[3:]
    if endBits > 0:
        binstring = binstring[:-endBits]

    coder = EliasOmegaCode()
    imageBytes = coder.decode(binstring)

    # If bits are not decoded correctly, return the input
    if len(imageBytes) != width * height * 3:
        return content

    # Even numbers should be positive. Odd numbers should be negative.
    differences = [x // 2 if x % 2 == 0 else -(x // 2) for x in imageBytes]
    pixels = [Pixel(int(differences[i + 2]), int(differences[i + 1]), int(differences[i])) for i in range(0,len(differences),3)]
    pixels = differential_decoding(pixels)
    pixels_array = []
    for p in pixels:
        pixels_array += [p.b, p.g, p.r]
    
    return content[:18] + bytes(pixels_array) + content[-26:]


def encode(content, k):
    width = int(content[13]) << 8 | (int(content[12]))
    height = int(content[15]) << 8 | (int(content[14]))
    imageBytes = content[18:-26]
    pixels = PixelsContainer(imageBytes, width, height)
    low_pass = [
        [1, 1, 1],
        [1, 1, 1],
        [1, 1, 1]
    ]
    high_pass = [
        [-1, -1, -1],
        [-1, 9, -1],
        [-1, -1, -1]
    ]
    filtered_low = [filter_pass(pixels, x, y, low_pass) for y in reversed(range(pixels.height)) for x in range(pixels.width)]
    filtered_high = [filter_pass(pixels, x, y, high_pass) for y in reversed(range(pixels.height)) for x in range(pixels.width)]
    
    # Flatten pixels to 1 dimension
    pixels_flat = [pixels[x, y] for y in reversed(range(pixels.height)) for x in range(pixels.width)]

    low_res = differential_coding(filtered_low)
    # Go back to the list of numbers
    byte_array = []
    for p in low_res:
        byte_array += [p.b, p.g, p.r]

    # Prepare for Elias coding (get rid of non-positive numbers)
    byte_array = [2 * x if x > 0 else abs(x) * 2 + 1 for x in byte_array]
    coder = EliasOmegaCode()
    binstring = ''.join([coder.encode(x) for x in byte_array])

    # Calculate how many bits at the end are useless and put this number at the beginning
    bitsToFill = 8 - ((len(binstring) + 3) % 8)
    bitsToFill %= 8
    s = '{0:03b}'.format(bitsToFill) + binstring
    s = s.ljust(len(s) + bitsToFill, '0')
    b = bytes(int(s[i : i + 8], 2) for i in range(0, len(s), 8))
    low_res_bytes = content[:18] + b + content[-26:]

    # Calculate the result for the high-pass filter
    high_res = quantize(filtered_high, k)
    byte_array = []
    for p in high_res:
        byte_array += [p.b, p.g, p.r]
    high_res_bytes = content[:18] + bytes(byte_array) + content[-26:]

    # Print stats
    low_mse, low_mse_r, low_mse_g, low_mse_b, low_snr = get_stats(pixels_flat, filtered_low)
    high_mse, high_mse_r, high_mse_g, high_mse_b, high_snr = get_stats(pixels_flat, high_res)

    print(f'Low MSE: {low_mse}')
    print(f'Low MSE (red): {low_mse_r}')
    print(f'Low MSE (green): {low_mse_g}')
    print(f'Low MSE (blue): {low_mse_b}')
    print(f'Low SNR: {low_snr} ({10 * math.log10(low_snr)} dB)')
    print(f'High MSE: {high_mse}')
    print(f'High MSE (red): {high_mse_r}')
    print(f'High MSE (green): {high_mse_g}')
    print(f'High MSE (blue): {high_mse_b}')
    print(f'High SNR: {high_snr} ({10 * math.log10(high_snr)} dB)')

    return low_res_bytes, high_res_bytes


def append_to_file_name(filename, extra):
    name, ext = os.path.splitext(filename)
    return "{name}_{extra}{ext}".format(name=name, extra=extra, ext=ext)


if len(sys.argv) < 4:
    print('Wrong parameters')
    print('python3 quants.py [input file] [output file] [--encode k|--decode]')
    sys.exit(2)

filename = sys.argv[1]
outfilename = sys.argv[2]
k = int(sys.argv[4]) if len(sys.argv) == 5 else -1
action = sys.argv[3]
infile = open(filename, mode='rb')
fileContent = infile.read()

if action == '--encode':
    if k == -1:
        print('Wrong parameters')
        print('python3 quants.py [input file] [output file] [--encode k|--decode]')
        sys.exit(2)
        
    low_res, high_res = encode(fileContent, k)
    outfile = open(append_to_file_name(outfilename, 'low_encoded'), mode='wb')
    outfile.write(low_res)
    outfile.close()

    outfile = open(append_to_file_name(outfilename, 'high'), mode='wb')
    outfile.write(high_res)
    outfile.close()
elif action == '--decode':
    res = decode(fileContent)
    outfile = open(outfilename, mode='wb')
    outfile.write(res)

    
