import RPi.GPIO as GPIO
import time
import serial
import board
import sys
import os

import json

import requests

# print("Loading members data")

# with open('member.json' , 'r') as reader:
#     members_data = json.loads(reader.read())


# for oled display
import Adafruit_SSD1306

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

FONT_SIZE = 14
TIME_FONT_SIZE = 24
DATE_FONT_SIZE = 15

disp = Adafruit_SSD1306.SSD1306_128_64(rst=0)

disp.begin()
disp.clear()
disp.display()

width = disp.width
height = disp.height

font=ImageFont.truetype("./fonts/ARIALUNI.TTF", FONT_SIZE)
lcd_font = ImageFont.truetype('./fonts/LCD-BOLD.TTF', size=TIME_FONT_SIZE)
lcd_font2 = ImageFont.truetype('./fonts/LCD-BOLD.TTF', size=DATE_FONT_SIZE)

startup_image = Image.new('1', (width, height))
idle_image = Image.new('1', (width, height))
auth_image = Image.new('1', (width, height))
fail_auth_image = Image.new('1', (width, height))

draw = ImageDraw.Draw(startup_image)

draw.text((25, 1*FONT_SIZE -1), 'Makerspace',  font=font, fill=255)
draw.text((20, 2*FONT_SIZE -1), '門禁系統 v1.0',  font=font, fill=255)


draw = ImageDraw.Draw(idle_image)

draw.text((10, 1*FONT_SIZE -1), '請將接近掃描指紋',  font=font, fill=255)


draw = ImageDraw.Draw(fail_auth_image)

draw.text((30, 1*FONT_SIZE -1), '指紋未授權',  font=font, fill=255)


draw = ImageDraw.Draw(auth_image)

draw.text((35, 1*FONT_SIZE -1), '門已開啟',  font=font, fill=255)

# import busio：
from digitalio import DigitalInOut, Direction
import adafruit_fingerprint

led = DigitalInOut(board.D13)
led.direction = Direction.OUTPUT

# uart = busio.UART(board.TX, board.RX, baudrate=57600)

# If using with a computer such as Linux/RaspberryPi, Mac, Windows with USB/serial converter:
# import serial
# uart = serial.Serial("/dev/ttyUSB0", baudrate=57600, timeout=1)

# If using with Linux/Raspberry Pi and hardware UART:
# import serial
# uart = serial.Serial("/dev/ttyS0", baudrate=57600, timeout=1)

# If using with Linux/Raspberry Pi 3 with pi3-disable-bt
# import serial
uart = serial.Serial("/dev/ttyS0", baudrate=57600, timeout=1)

finger = adafruit_fingerprint.Adafruit_Fingerprint(uart)

door_lock_pin = 17


GPIO.setmode(GPIO.BCM)
GPIO.setup(door_lock_pin,GPIO.OUT)
correct=False


BASE_URL = 'http://140.112.174.222:8080'
# self.login_data = {'user' : '', 'pass' : ''}
# self.IsLoginIn = False
USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36'

session = requests.Session()
session.headers = {'user-agent' : USER_AGENT}



def get_fingerprint():
    """Get a finger print image, template it, and see if it matches!"""
    print("Waiting for image...")
    while finger.get_image() != adafruit_fingerprint.OK:
        pass
    print("Templating...")
    if finger.image_2_tz(1) != adafruit_fingerprint.OK:
        return False
    print("Searching...")
    if finger.finger_search() != adafruit_fingerprint.OK:
        return False
    return True

def draw_message(line_no,msg):
    start_pos = (disp.width // FONT_SIZE - len(msg)) // 2
    draw.text((start_pos,max(line_no*FONT_SIZE-1,0)),msg,font=font,fill=255)
    print(start_pos,max(line_no*FONT_SIZE-1,0))
    

disp.image(startup_image)
disp.display()

time.sleep(2)
disp.clear()
disp.display()



while (1):
    # get time
    t = time.localtime()
    current_date = time.strftime("%Y/%m/%d", t)
    current_time = time.strftime("%H : %M : %S", t)
    time_img = Image.new('1', (width, height))
    time_draw = ImageDraw.Draw(time_img)
    time_draw.text((5, 30), current_time, font=lcd_font, fill=255)
    time_draw.text((25, 5), current_date, font=lcd_font2, fill=255)
    
    disp.clear()
    disp.display()

    # disp.image(idle_image)
    disp.image(time_img)
    disp.display()

    correct = False

    print("----------------")
    if finger.read_templates() != adafruit_fingerprint.OK:
        raise RuntimeError("Failed to read templates")
    print("Fingerprint templates: ", finger.templates)
    if finger.count_templates() != adafruit_fingerprint.OK:
        raise RuntimeError("Failed to read templates")
    print("Number of templates found: ", finger.template_count)
    if finger.read_sysparam() != adafruit_fingerprint.OK:
        raise RuntimeError("Failed to get system parameters")

    if get_fingerprint():        
        print("Detected #", finger.finger_id, "with confidence", finger.confidence)
        correct=True
    else:
        print("Finger not found")
        disp.clear()
        disp.display()
        disp.image(fail_auth_image)
        disp.display()

    if correct==True:
        print("======================")
        
        

        # if finger.finger_id < len(members_data['members']) :
        print("get finger id:{}".format(finger.finger_id))
        print("connecting to server")
        API_AUTH = '/api/machine/getUser'

        _data = {'finger_id' : finger.finger_id}

        req = session.post(BASE_URL+API_AUTH,data=_data,allow_redirects = True)
        
        req = json.loads(req.text)
        disp.clear()
        disp.display()
        print("Get request",req)
        if(req['status']=="success"):
            if not req['data'] == "no user":
                user_data = req['data'][0]
                if user_data[2] == "admin" or user_data[2] == "mks_member":
                    
                    disp_id_image = Image.new('1', (width, height))

                    draw = ImageDraw.Draw(disp_id_image)

                    draw.text((5, 1*FONT_SIZE -1), '{}  {}'.format(user_data[1],user_data[4]),  font=font, fill=255)
                    draw.text((15, 2*FONT_SIZE -1), '{}'.format(user_data[5]),  font=font, fill=255)

                    disp.image(disp_id_image)
                    disp.display()


                    GPIO.output(door_lock_pin, GPIO.HIGH)
                    time.sleep(0.5)
                    GPIO.output(door_lock_pin, GPIO.LOW)
                    time.sleep(0.2)
                else:
                    disp_id_image = Image.new('1', (width, height))

                    draw = ImageDraw.Draw(disp_id_image)

                    draw.text((5, 1*FONT_SIZE -1), '{}  {}'.format(user_data[1],user_data[4]),  font=font, fill=255)
                    draw.text((15, 2*FONT_SIZE -1), '{}'.format(user_data[5]),  font=font, fill=255)
                    draw.text((15, 3*FONT_SIZE -1), '{}'.format("未開放門禁"),  font=font, fill=255)
                    disp.image(disp_id_image)
                    disp.display()
            else:
                print("finger_id:{} not on server".format(finger.finger_id))
                disp_id_image = Image.new('1', (width, height))

                draw = ImageDraw.Draw(disp_id_image)

                draw.text((5, 1*FONT_SIZE -1), '伺服器無資料',  font=font, fill=255)        
        else:
            disp_id_image = Image.new('1', (width, height))

            draw = ImageDraw.Draw(disp_id_image)

            draw.text((5, 1*FONT_SIZE -1), '伺服器錯誤',  font=font, fill=255)

            disp.image(disp_id_image)
            disp.display()
            

    else :
        time.sleep(0.2)

    time.sleep(1)
