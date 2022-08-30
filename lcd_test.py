# LCD Display test of Adafruit LoRaWAN Bonnett
#


import time
import busio
from digitalio import DigitalInOut, Direction, Pull
from PIL import Image
import board
import adafruit_ssd1306
import adafruit_rfm9x
import os
import json
import psutil
import signal
import sys
import RPi.GPIO as GPIO

# Button A
btnA = DigitalInOut(board.D5)
btnA.direction = Direction.INPUT
btnA.pull = Pull.UP

# Button B
btnB = DigitalInOut(board.D6)
btnB.direction = Direction.INPUT
btnB.pull = Pull.UP

# Button C
btnC = DigitalInOut(board.D12)
btnC.direction = Direction.INPUT
btnC.pull = Pull.UP

# Create the I2C interface.
i2c = busio.I2C(board.SCL, board.SDA)

# 128x32 OLED Display
reset_pin = DigitalInOut(board.D4)
display = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c, reset=reset_pin)

image = Image.open('data_bridge_logo_black_small.png').resize((display.width, display.height), Image.ANTIALIAS).convert('1')

# Clear the display.
display.image(image)
display.show()
width = display.width
height = display.height
selected_page = 'pi'


# Show splash screen logo for few seconds

time.sleep(2.0)

# Callbacks for button presses

def button1_callback(channel):
    global selected_page
    selected_page = 'pi'

def button2_callback(channel):
    global selected_page
    selected_page = 'subsystem'

def button3_callback(channel):
    global selected_page
    selected_page = 'subsystem'

# Helper functions

def signal_handler(sig,frame):
    GPIO.cleanup()
    sys.exit(0)

def get_wlan_ip():

    ip = 'not assigned'
    routes = json.loads(os.popen("ip -j -4 route").read())

    for r in routes:
        if r.get("dev") == "wlan0" and r.get("prefsrc"):
            ip = r['prefsrc']
            continue

    return ip

def get_eth_ip():

    ip = 'not assigned'
    routes = json.loads(os.popen("ip -j -4 route").read())

    for r in routes:
        if r.get("dev") == "eth0" and r.get("prefsrc"):
            ip = r['prefsrc']
            continue

    return ip

def get_cpu_percent():
    return str(psutil.cpu_percent())

def get_avail_mem():

    avail_mem = psutil.virtual_memory().available * 100 / psutil.virtual_memory().total
    return str("{:.2f}".format(avail_mem))

def get_zigbee2mqtt_status():
    status = 'running'
    # TODO: fetch status from redis
    return status

def get_lorawan_status():
    status = 'joined'

    # TODO: fetch status from redis
    return status

def display_pi_status():


    display.fill(0)
    display.text('wlan0:'+get_wlan_ip(), 3,0,1)
    display.text('eth0:'+get_eth_ip(), 3,8,1)
    display.text('CPU:'+get_cpu_percent()+'%',3,16,1)
    display.text('Avail mem:'+get_avail_mem()+'%',3,24,1)
    display.show()

def display_subsystem_status():

    display.fill(0)
    display.text('zigbee2mqtt:'+get_zigbee2mqtt_status(),3,0,1)
    display.text('LoRaWAN TX:'+get_lorawan_status(),3,8,1)
    display.show()

def setup_button_callbacks():
    GPIO.setmode(GPIO.BCM)
    # Adafruit bonnet gpio numbers: Button1 - 5, Button2 - 6, Button3 - 12
    GPIO.setup(5, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(6, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(12, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    GPIO.add_event_detect(5, GPIO.FALLING,
            callback=button1_callback, bouncetime=100)
    GPIO.add_event_detect(6, GPIO.FALLING,
            callback=button2_callback, bouncetime=100)
    GPIO.add_event_detect(12, GPIO.FALLING,
            callback=button3_callback, bouncetime=100)

    signal.signal(signal.SIGINT, signal_handler)


setup_button_callbacks()


while True:

    # Check buttons
    #if not btnA.value:
        # Button A Pressed
    #    selected_page = 'pi'
    #if not btnB.value:
        # Button B Pressed
    #    selected_page = 'subsystem'
    #if not btnC.value:
        # Button C Pressed
    #    display.text('Radio', width-65, height-7, 1)
    #    display.show()
    #    time.sleep(0.1)

    if selected_page == 'subsystem':
        display_subsystem_status()
        time.sleep(0.5)

    if selected_page == 'pi':
        display_pi_status()
        time.sleep(0.5)
