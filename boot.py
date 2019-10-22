
# This file is executed on every boot (including wake-boot from deepsleep)

import time
from umqttsimple import MQTTClient

import ubinascii
import machine
import micropython
import network
import esp
esp.osdebug(None)
import gc
gc.collect()


ssid = 'P2797-24'
password = 'z0BcfpHu'
mqtt_server = '192.168.137.1'

client_id = ubinascii.hexlify(machine.unique_id())

redPin = machine.Pin(15, machine.Pin.OUT)
greenPin = machine.Pin(12, machine.Pin.OUT)
bluePin = machine.Pin(13, machine.Pin.OUT)

pinSTR = machine.Pin(15, machine.Pin.OUT) # Временное решение - красный дублирует сирену.
pinLGT = machine.Pin(12, machine.Pin.OUT) # Временное решение - зелёный дублирует белый свет.

topic_sub = b'RGB'
topic_pub = b'RGBASK'

last_message = 0
message_interval = 5
counter = 0

station = network.WLAN(network.STA_IF)

station.active(True)
station.connect(ssid, password)

while station.isconnected() == False:
  for x in range (4):
    redPin.value(1)
    time.sleep_ms(250)
    redPin.value(0)
    time.sleep_ms(250)
  pass

myMAC = ubinascii.hexlify(network.WLAN().config('mac'))  
redPin.value(0)
print('Connection successful')
print(station.ifconfig())
topic_sub_id = b'RGB/'+myMAC


