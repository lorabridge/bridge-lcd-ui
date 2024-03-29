#
# LoRaBridge:
#
# LCD Display UI controller script for Adafruit LoRaWAN Bonnett
#
# H. Ruotsalainen, 08/2022

import time
import busio
from digitalio import DigitalInOut, Direction, Pull
from PIL import Image
import board
import adafruit_ssd1306
import os
import json
import psutil
import signal
import sys
import RPi.GPIO as GPIO
import redis
import paho.mqtt.client as mqtt

# Parameters

MQTT_HOST = os.environ.get('FOR_MQTT_HOST', '127.0.0.1')
MQTT_PORT = int(os.environ.get('FOR_MQTT_PORT', 1883))
# MQTT_USERNAME = get_fileenv('FOR_MQTT_USERNAME') or 'lorabridge'
# MQTT_PASSWORD = get_fileenv('FOR_MQTT_PASSWORD') or 'lorabridge'
MQTT_BASE_TOPIC = os.environ.get('FOR_MQTT_BASE_TOPIC', 'zigbee2mqtt') + '/bridge'
# MQTT_SUB_TOPIC = os.environ.get('FOR_MQTT_SUB_TOPIC', 'lorabridge')
REDIS_HOST = os.environ.get('FOR_REDIS_HOST', "localhost")
REDIS_PORT = int(os.environ.get('FOR_REDIS_PORT', 6379))
REDIS_DB = int(os.environ.get('FOR_REDIS_DB', 0))
Z2M_STATUS = "undefined"
Z2M_CONNECTED_DEVICES = "undefined"
Z2M_JOIN_TIMEOUT = int(os.environ.get('LCD_Z2M_TIMEOUT', 300))

current_join_timeout = Z2M_JOIN_TIMEOUT
selected_page = 'pi'

# MQTT
# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(MQTT_BASE_TOPIC + '/#')


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    global Z2M_STATUS, Z2M_CONNECTED_DEVICES, selected_page
    if msg.topic != None and "state" in msg.topic:
        Z2M_STATUS = msg.payload.decode('utf-8')

    if msg.topic != None and "devices" in msg.topic:
        # only end devices, no e.g. coordinator
        payload = [dev for dev in json.loads(msg.payload) if dev['type'] != 'Coordinator']
        Z2M_CONNECTED_DEVICES = str(len(payload))

    if msg.topic != None and "event" in msg.topic:
        event_payload = json.loads(msg.payload)
        if event_payload['type'] == "device_joined":
            selected_page = 'device_joined'

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(MQTT_HOST, MQTT_PORT, 60)
r_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)
client.user_data_set({"topic": MQTT_BASE_TOPIC})
client.loop_start()

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

image = Image.open('data_bridge_logo_black_small.png').resize((display.width, display.height),
                                                              Image.Resampling.LANCZOS).convert('1')

# Clear the display.
display.image(image)
display.show()
width = display.width
height = display.height


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
    global current_join_timeout
    current_join_timeout = Z2M_JOIN_TIMEOUT
    selected_page = 'joining'
    permit_join()


# Helper functions


def signal_handler(sig, frame):
    GPIO.cleanup()
    sys.exit(0)


def permit_join():
    client.publish(MQTT_BASE_TOPIC + "/request/permit_join", json.dumps({"value": True, "time": Z2M_JOIN_TIMEOUT}))


def get_ips():
    data = filter(None, open("/ofelia/ips").read().split("\n"))
    return {x.split("dev")[1].strip().split(" ")[0]: x.split("src")[1].strip().split(" ")[0] for x in data}


def get_cpu_percent():
    return str(psutil.cpu_percent())


def get_avail_mem():

    avail_mem = psutil.virtual_memory().available * 100 / psutil.virtual_memory().total
    return str("{:.2f}".format(avail_mem))


def get_zigbee2mqtt_status():
    status = Z2M_STATUS
    return status


def get_lorawan_status():
    status = 'undefined'

    status_new = r_client.get("txstatus")

    if status_new:
        status = status_new

    return status

def get_tx_queue_status():
    status = 'undefined'

    # status_new = str(r_client.llen("lorabridge_data"))
    status_new = str(len(r_client.keys("lorabridge:device:*:message:*")))
    if status_new:
        status = status_new

    return status

def display_pi_status():

    display.fill(0)

    # IP Address fetchig to be implemented
    ips = get_ips()
    #display.text('wlan0:'+get_wlan_ip(), 3,0,1)
    #display.text('eth0:'+get_eth_ip(), 3,8,1)
    display.text('wlan0:' + ips.get('wlan0', 'unconfigured'), 3, 0, 1)
    display.text('eth0:' + ips.get('eth0', 'unconfigured'), 3, 8, 1)

    display.text('CPU:' + get_cpu_percent() + '%', 3, 16, 1)
    display.text('Avail mem:' + get_avail_mem() + '%', 3, 24, 1)
    display.show()


def display_subsystem_status():

    display.fill(0)
    display.text('zigbee2mqtt:' + get_zigbee2mqtt_status(), 3, 0, 1)
    display.text('zigbee devices:' + Z2M_CONNECTED_DEVICES, 3, 8, 1)
    display.text('LoRaWAN TX:' + get_lorawan_status(), 3, 16, 1)
    display.text('TX queue length:'+get_tx_queue_status(),3,24,1)
    display.show()


def display_joining_timeout():
    display.fill(0)
    display.text('Joining enabled: ' + str(current_join_timeout) + " s", 3, 8, 1)
    display.show()


def display_device_joined():
    display.fill(0)
    display.text('Zigbee device joined!', 3,8,1)
    display.show()
    time.sleep(2.0)


def setup_button_callbacks():
    GPIO.setmode(GPIO.BCM)
    # Adafruit bonnet gpio numbers: Button1 - 5, Button2 - 6, Button3 - 12
    GPIO.setup(5, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(6, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(12, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    GPIO.add_event_detect(5, GPIO.FALLING, callback=button1_callback, bouncetime=100)
    GPIO.add_event_detect(6, GPIO.FALLING, callback=button2_callback, bouncetime=100)
    GPIO.add_event_detect(12, GPIO.FALLING, callback=button3_callback, bouncetime=100)

    signal.signal(signal.SIGINT, signal_handler)


setup_button_callbacks()

while True:



    if selected_page == 'subsystem':
        display_subsystem_status()
        time.sleep(0.5)

    if selected_page == 'pi':
        display_pi_status()
        time.sleep(0.5)

    if selected_page == 'joining':
        display_joining_timeout()
        time.sleep(1)
        if current_join_timeout > 0:
            current_join_timeout -= 1
        else:
            selected_page = 'subsystem'

    if selected_page == 'device_joined':
        display_device_joined()
        time.sleep(2.0)
        selected_page = 'pi'
