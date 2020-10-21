import time

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

width = 128
height = 64

font_size = 24
lcd_font = ImageFont.truetype('./fonts/LCD-BOLD.TTF', size=font_size)

test_img = Image.new('1', (width, height))

test_draw = ImageDraw.Draw(test_img)

test_draw.text((5, font_size - 1), '12 : 34 : 56', font=lcd_font, fill=255)

test_img.show()