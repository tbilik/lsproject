#!/usr/bin/python

# imports
import obd
from obd import OBDStatus
import board
import os
import time
from datetime import datetime
import digitalio
import random
import csv
import math
from digitalio import DigitalInOut, Direction, Pull
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306

# this function is called to receive data from a certain PID
def retrieveData(pid):
    return connection.query(obd.commands[pid]).value

# this function returns an array of data from several PIDs
def retrieveOBD():
    returnArray = []
    returnArray.append(secondsSinceEpoch - startingTime) # program runtime (you could use runtime PID, but it's not supported on my vehicle)
    returnArray.append(retrieveData("SPEED").to("mph").magnitude) # speed
    returnArray.append(retrieveData("RPM").magnitude) # rpm
    returnArray.append(retrieveData("COOLANT_TEMP").to("fahrenheit").magnitude) # temperature
    returnArray.append(retrieveData("MAF").magnitude) # mass air flow
    returnArray.append(retrieveData("ENGINE_LOAD").magnitude) # engine load
    returnArray.append(retrieveData("INTAKE_TEMP").to("fahrenheit").magnitude) # intake air temperature
    return returnArray

# this function will display data to the oled screen, it takes mode and data as input parameters
def displayOutput(mode, data):
    if mode == 0:
        firstLine = "VSS: " + str(math.floor(data[1])) + " mph"
        secondLine = "ESS: " + str(math.floor(data[2])) + " RPM"
        thirdLine = "CT: " + str(math.floor(data[3])) + " F"
    elif mode == 1:
        firstLine = "EL: " + str(math.floor(data[5])) + "%"
        secondLine = "MAF: " + str(math.floor(data[4])) + " g/s"
        thirdLine = "IT: " + str(math.floor(data[6])) + " F"
    elif mode == 2:
        firstLine = "Car " + str(currentCar)
        secondLine = "Uptime:"
        thirdLine = str(data[0]) + " s"
    draw.rectangle((0, 0, oled.width, oled.height * 2), outline=0, fill=0)
    draw.text((0,0), firstLine, font=font, fill=255)
    draw.text((0,18), secondLine, font=font, fill=255)
    draw.text((0,36), thirdLine, font=font, fill=255)
    oled.image(image)
    oled.show()
        

# i2c interface and display
i2c = board.I2C()
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

# create image and font
image = Image.new('1', (oled.width, oled.height))
draw = ImageDraw.Draw(image)
font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 16)

# startup screen
oled.fill(0)
draw.rectangle((0, 0, oled.width, oled.height * 2), outline=0, fill=0)
draw.text((0,0), "Starting up", font=font, fill=255)
draw.text((0,18), "Program...", font=font, fill=255)
oled.image(image)
oled.show()

# this code is deprecated. It works, but connection is intermitent.
# enable connection to OBD-II, continue trying to connect if connection isn't established
#tryAgain = True
#while tryAgain:
#    try:
#        connection = obd.Async(fast=False, timeout=30)
#        tryAgain = False
#    except:
#        time.sleep(1) # if connection couldn't be established, wait a second

#while True:
#    if connection.status() == OBDStatus.CAR_CONNECTED:
#        break

# connect to ELM327 OBD-II interface chip
while True:
    try:
        connection = obd.Async(fast=False,timeout=30)
        if connection.status() == OBDStatus.CAR_CONNECTED:
            break
    except:
        # this code runs if the connection fails in some way
        print("Connection failed. Trying again ...") # this is for the log file
        # this is the screen output
        draw.rectangle((0, 0, oled.width, oled.height * 2), outline=0, fill=0)
        draw.text((0,0), "Connection", font=font, fill=255)
        draw.text((0,18), "failed. Trying", font=font, fill=255)
        draw.text((0,36), "again ...", font=font, fill=255)
        oled.image(image)
        oled.show()

# connection data to track
connection.watch(obd.commands["SPEED"])
connection.watch(obd.commands["RPM"])
connection.watch(obd.commands["COOLANT_TEMP"])
connection.watch(obd.commands["MAF"])
connection.watch(obd.commands["ENGINE_LOAD"])
connection.watch(obd.commands["INTAKE_TEMP"])

# start connection of interface chip with vehicle
connection.start()
# approximately 2 seconds needed to stabilize connection
time.sleep(2)

# various variables
currentMode = 0
currentCar = 1
maxMode = 2
allLogs = []
leftJoyletgo = True
rightJoyletgo = True
rightButtonletgo = True
metric = False
# note: time.time() does work as well, but can result in large skips if the system clock is changed on startup
startingTime = int(time.monotonic())
secondsSinceEpoch = 0


while True:
    # if left joystick is pressed, change mode (decrease mode by 1)
    if not leftJoy.value and leftJoyletgo:
        currentMode = maxMode if currentMode == 0 else currentMode - 1
        displayOutput(currentMode, allLogs[-1])
        leftJoyletgo = False

    if leftJoy.value:
        leftJoyletgo = True

    # if right joystick is pressed, change mode (increase mode by 1)
    if not rightJoy.value and rightJoyletgo:
        currentMode = 0 if currentMode == maxMode else currentMode + 1
        displayOutput(currentMode, allLogs[-1])
        rightJoyletgo = False

    if rightJoy.value:
        rightJoyletgo = True

    # every second (without using sleep), update the logs and display data
    if secondsSinceEpoch != int(time.monotonic()):
        while connection.status() != OBDStatus.CAR_CONNECTED:
            draw.rectangle((0,0, oled.width, oled.height * 2), outline=0, fill=0)
            draw.text((0,0), "Waiting for", font=font, fill=255)
            draw.text((0,18), "connection.", font=font, fill=255)
            oled.image(image)
            oled.show()
        secondsSinceEpoch = int(time.monotonic())
        allLogs.append(retrieveOBD())
        displayOutput(currentMode, allLogs[-1])

    # if left button is pressed, save logs, upload logs, and exit
    if not leftButton.value:
        draw.rectangle((0, 0, oled.width, oled.height * 2), outline=0, fill=0)
        draw.text((0,0), "Saving logs ...", font=font, fill=255)
        oled.image(image)
        oled.show()

        if not os.path.exists("/home/pi/logs"):
            os.makedirs("/home/pi/logs")

        os.chdir("/home/pi/logs")
        
        # if car directory doesn't exist, create it
        if not os.path.exists(str(currentCar)):
            os.makedirs(str(currentCar))

        # write to file
        with open(str(currentCar) + "/" + datetime.now().strftime("%Y%m%d%H%M%S.csv"), "w+") as my_csv:
            csvWriter = csv.writer(my_csv,delimiter=',')
            csvWriter.writerows(allLogs)
            
        draw.text((0,18), "Uploading logs ...", font=font, fill=255)
        oled.image(image)
        oled.show()
        # upload via git
        os.system("git add .")
        os.system("git commit -m 'auto commit'")
        os.system("git push origin master")
        draw.text((0,36), "Shutting down ...", font=font, fill=255)
        oled.image(image)
        oled.show()
        connection.stop()
        os.system("/sbin/shutdown now")
        exit()

    if not rightButton.value and rightButtonletgo:
        currentCar = 1 if currentCar == 9 else currentCar + 1
        displayOutput(currentMode, allLogs[-1])
        rightButtonletgo = False

    if rightButton.value:
        rightButtonletgo = True
