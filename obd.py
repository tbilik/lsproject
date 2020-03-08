#!/usr/bin/python

# imports
# import obd
import board
from digitalio import DigitalInOut, Direction, Pull
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306

# i2c interface and display
i2c = busio.I2C(board.SCL, board.SDA)
RESET_PIN = digitalio.DigitalInOut(board.D4)
oled = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c, addr=0x3c, reset=RESET_PIN)

# button and joystick input
leftButton = DigitalInOut(board.D5)
leftButton.direction = Direction.INPUT
leftButton.pull = Pull.UP
 
rightButton = DigitalInOut(board.D6)
rightButton.direction = Direction.INPUT
rightButton.pull = Pull.UP
 
leftJoy = DigitalInOut(board.D27)
leftJoy.direction = Direction.INPUT
leftJoy.pull = Pull.UP
 
rightJoy = DigitalInOut(board.D23)
rightJoy.direction = Direction.INPUT
rightJoy.pull = Pull.UP
 
upJoy = DigitalInOut(board.D17)
upJoy.direction = Direction.INPUT
upJoy.pull = Pull.UP
 
downJoy = DigitalInOut(board.D22)
downJoy.direction = Direction.INPUT
downJoy.pull = Pull.UP
 
pressJoy = DigitalInOut(board.D4)
pressJoy.direction = Direction.INPUT
pressJoy.pull = Pull.UP

# enable connection to OBD-II
# connection = obd.OBD();

# Clear display
oled.fill(0)
oled.show()

image = Image.new('1', (oled.width, oled.height))
draw = ImageDraw.Draw(image)
font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 16)

while True:
    draw.rectangle((0, 0, oled.width, oled.height * 2), outline=0, fill=0)
    firstLine = "Vehicle Speed: 0 mph"
    secondLine = "Engine Speed: 900 RPM"
    thirdLine = "Engine Temp: 190 F"
    draw.text((0,0), firstLine, font=font, fill=255)
    draw.text((0,18), secondLine, font=font, fill=255)
    draw.text((0,36), thirdLine, font=font, fill=255)
    time.sleep(1)
    
