import machine
from network import WLAN
from ubinascii import hexlify

ENV = 'dev'  # устанавливаем переменную окружения

# все реюзабельные штуки стоит упаковать в словарь и дергать по ключу,
# чтобы не импортировать из модуля в модуль кучу переменных, в том числе

cfg = {
    'broker_ip': '192.168.137.1',
    'client_id': hexlify(machine.unique_id()),
    'mac': hexlify(WLAN().config('mac')),
    'last_message': 0,
    'message_interval': 5,
    'counter': 0,
    'wlan_ssid': 'P2797-24',  # имена длинные, зато точно все понятно
    'wlan_password': 'z0BcfpHu'
}

# точно так же упаковываем пины
pins = {
    'red': machine.Pin(15, machine.Pin.OUT),
    'green': machine.Pin(12, machine.Pin.OUT),
    'blue': machine.Pin(13, machine.Pin.OUT),
    'STR': machine.Pin(15, machine.Pin.OUT),  # сирена на красном пине
    'LGT': machine.Pin(12, machine.Pin.OUT)  # белый свет на зеленом пине
}

# и топики
topics = {
    'sub': b'RGB',
    'pub': b'RGBASK',
    'pub_id': b'RGBASK/' + cfg['mac'],
    'sub_id': b'RGB/' + cfg['mac']
}

"""

    Теперь можно добавить все пины и топики в конфиг, в случае если у нас 
    этим конфигом будут пользоваться разные модули и не всегда понятно, 
    какие части из него кому пригодятся. 

    config['topic'] = topic
    config['pins'] = pins

    но у нас мелкое приложение и можно этого не делать
"""

# и собираем словарь для PWM при помощи dictionary comprehension
pwm = {p: machine.PWM(p, freq=1000) for p in pins
       if p in ('red', 'green', 'blue')}