import machine
from network import WLAN
from ubinascii import hexlify

ENV = 'dev'  

cfg = {
    'broker_ip': '192.168.137.1',
    'client_id': hexlify(machine.unique_id()),
    'mac': hexlify(WLAN().config('mac')),
    'last_message': 0,
    'message_interval': 5,
    'counter': 0,
    'wlan_ssid': 'P2797-24',  
    'wlan_password': 'z0BcfpHu',
    'quant_num': 50,
}

pins = {
    'red': machine.Pin(15, machine.Pin.OUT),
    'green': machine.Pin(12, machine.Pin.OUT),
    'blue': machine.Pin(13, machine.Pin.OUT),
    'STR': machine.Pin(15, machine.Pin.OUT),  
    'LGT': machine.Pin(12, machine.Pin.OUT)  
}

topics = {
    'sub': b'rgb/all',
    'sub_id': b'rgb/' + cfg['mac'],
    'pub': b'ask/rgb/' + cfg['mac'] + b'/SUP',
}

commands = {
    "online": b'{"online"}',
    "ping": b'{"ping"}',
    "offline": b'{"offline"}'
}

