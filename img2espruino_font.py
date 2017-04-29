#!/usr/bin/env python3
"""
converts an image into a bitmap font for espruino

see https://www.espruino.com/Fonts for more details

syntax:
 <this_script.py> IMAGE_FILE.png WIDTH FIRST_CHARACTER

by default character width is fixed, if you want to change it,
check note inside the code.

"""
from PIL import Image
from binascii import b2a_base64
from collections import defaultdict
import sys

if len(sys.argv) != 4:
    print('Run with the following arguments: ')
    print('{0} IMAGE_FILE.png WIDTH FIRST_CHARACTER'.format(sys.argv[0]))
    print('ex.: {0} font.png 6 "a"'.format(sys.argv[0]))
    sys.exit(1)
else:
    imagefile, width, first_character = sys.argv[1:]

img = Image.open(imagefile)
default_width = int(width)
start_char = ord(first_character[0])

height = img.height

img_rotated = img.rotate(90, expand=True)
img_rotated_flipped = img_rotated.transpose(Image.FLIP_TOP_BOTTOM)

bin_data = bytearray()
byte_data = 0
for index, x in enumerate(img_rotated_flipped.getdata(0), start=1):
    byte_data <<= 1
    byte_data |= 0 if x else 1
    if not (index % 8):
        bin_data.append(byte_data)
        byte_data = 0

bin_data.append(byte_data << 8-(index % 8))

widths = defaultdict(lambda: default_width)

# uncomment and modify paragraph below
# to enable variable character width
"""
widths.update({
               '!': 2,
               '"': 4,
               "'": 2,
               '0': 4,
               'h': 4,
               'm': 5,
               'n': 4,
               'u': 4,
               'v': 4,
               'w': 4,
               'x': 4,
               'y': 4,
               'i': 2,
               })
               """

widths_data = bytearray()
for char_index in range(start_char, img.width):
    width = widths[chr(char_index)]
    widths_data.append(width)

print('''var font = atob("{0}");'''.format(str(b2a_base64(bin_data),
                                               'ascii').strip()))
if len(set(widths.values())) > 1:
    print('''var widths = atob("{0}");'''.format(str(b2a_base64(widths_data),
                                                     'ascii').strip()))
    print('''g.setFontCustom(font, {0}, widths, {1});'''.format(start_char,
                                                                height))
else:
    default_width = "widths" if default_width == 0 else default_width
    print('''g.setFontCustom(font, {0}, {1}, {2});'''.format(start_char,
                                                             default_width,
                                                             height))
