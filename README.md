LCD User Interface of Bridge Unit
============================================
This repository is part of the LoRaBridge project.

This repository contains source code, which implements a simplified LCD/push button based user interface
for the Bridge PI. Via the UI, an user can access some relevant information such as the status of the LoRaWAN
link or pairing events of Zigbee Devices.

Features
--------
- Enable allow join state for ZigBee2MQTT
- Display LoRaWAN Link status
- Display ZigBee2MQTT status
- Display IP addresses of wlan0/eth0 of the Bridge PI
- Display number of joined ZigBee devices
- Display ZigBee join events
- Display LoRaWAN transmit queue length

Supported hardware
------------------

Adafruit LoRa Radio Bonnet with OLED 868/915 MHz

## Environment Variables
- `FOR_MQTT_HOST`: IP or hostname of MQTT host
- `FOR_MQTT_PORT`: Port used by MQTT
- `FOR_MQTT_BASE_TOPIC`: MQTT topic used by zigbee2mqtt (default: `zigbee2mqtt`)
- `FOR_REDIS_HOST`: IP or hostname of Redis host
- `FOR_REDIS_PORT`: Port used by Redis
- `FOR_REDIS_DB`: Number of the database used inside Redis
- `LCD_Z2M_TIMEOUT`: Timeout in seconds for permitting zigbee join requests

## License

All the LoRaBridge software components and the documentation are licensed under GNU General Public License 3.0.

## Acknowledgements

The financial support from Internetstiftung/Netidee is gratefully acknowledged. The mission of Netidee is to support development of open-source tools for more accessible and versatile use of the Internet in Austria.
