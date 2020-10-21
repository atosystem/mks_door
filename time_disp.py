import sys
import time

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
# from time import sleep

width = 128
height = 64

font_size = 24
lcd_font = ImageFont.truetype('./fonts/LCD-BOLD.TTF', size=font_size)
lcd_font2 = ImageFont.truetype('./fonts/LCD-BOLD.TTF', size=15)


while True:
    t = time.localtime()
    current_date = time.strftime("%Y/%m/%d", t)
    current_time = time.strftime("%H : %M : %S", t)
    print(current_time)

    test_img = Image.new('1', (width, height))
    test_draw = ImageDraw.Draw(test_img)

    test_draw.text((5, 30), current_time, font=lcd_font, fill=255)
    test_draw.text((25, 5), current_date, font=lcd_font2, fill=255)
    
    time.sleep(1)

    test_img.show()