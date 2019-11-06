
# This file is executed on every boot (including wake-boot from deepsleep)

import time
import esp
import gc
# импортируем только те модули, которые нужны
from network import WLAN, STA_IF

esp.osdebug(None)
gc.collect()

# отделили конфиг в отдельный файл
import config

station = WLAN(STA_IF)
station.active(True)
station.connect(config.cfg['wlan_ssid'], config.cfg['wlan_password'])

signal_pin = config.pins['red']  # здесь создается только ссылка на словарь

while station.isconnected() == False:
    for x in range (4):
        signal_pin.value(1)
        time.sleep(.25)
        signal_pin.value(0)
        time.sleep(.25)

print('Connection successful')
print(station.ifconfig())
signal_pin.value(0)

