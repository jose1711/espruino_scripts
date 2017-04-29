#!/usr/bin/env python3
"""
helps to convert a truetype font into
espruino bitmap font

more at https://www.espruino.com/Fonts

how to use:

- run with two arguments:
    full path to ttf font file (e. g. /usr/share/fonts/TTF/arial.ttf on Linux)
    size of the font in points (e. g. 18)
- copy and paste the line with `var widths` into espruino IDE
- run img2espruino_font.py as suggested in the next line
- put the output right below the previously pasted line
- test it with g.drawString('some text', x, y)

known issues:

- small fonts look jagged - i don't think this can be fixed easily. freetype
                            library used simply rely on the fact that text is
                            no longer bicolor

- slanted fonts will look bad - stay away from them

- thanks to font hinting and kerning various artifacts may appear - you may
  want to review the png image before feeding it to img2espruino_font.py script

"""
from PIL import Image, ImageFont, ImageDraw, ImageOps
from binascii import b2a_base64
from tempfile import mktemp
import sys
import logging

logging.basicConfig(level=logging.INFO)

try:
    fontname, fontsize = sys.argv[1:]
except ValueError:
    print('Supply path to ttf font and size as arguments.')
    print('Example: {0} /usr/share/fonts/TTF/arial.ttf 13'.format(sys.argv[0]))
    sys.exit(1)

fontsize = int(fontsize)
font = ImageFont.truetype(fontname, fontsize)

max_width = 8000
max_height = 1024

text = ''
old_width = 0
widths_data = bytearray()

for i in range(33, 127):
    text += chr(i)
    img = Image.new('RGBA', (max_width, max_height))
    draw = ImageDraw.Draw(img)
    draw.text((0, 0), text, font=font)
    img = img.convert(mode='1')
    img = img.crop(img.getbbox())
    logging.debug(chr(i), img.width - old_width)
    if 'n' in chr(i):
        space_width = img.width - old_width
    widths_data.append(img.width - old_width)
    old_width = img.width

img = Image.new('RGBA', (max_width, max_height))
draw = ImageDraw.Draw(img)
all_ascii = ''.join([chr(x) for x in range(33, 127)])
draw.text((30, 0), all_ascii, font=font)
img = img.convert(mode='L')
bbox = list(img.getbbox())
bbox[0] -= space_width
img = img.crop(bbox)
img = ImageOps.invert(img)
img = img.convert(mode='1')
widths_data.insert(0, space_width)
print('''var widths = atob("{0}");'''.format(str(b2a_base64(widths_data),
                                             'ascii').strip()))
output_file = mktemp(suffix='.png')
img.save(output_file)
print('\nNow run img2espruino_font.py {0} 0 " "'.format(output_file))
