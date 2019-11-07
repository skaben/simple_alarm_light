
import machine
from network import WLAN
from ubinascii import hexlify

ENV = 'dev'  # 褍褋褌邪薪邪胁谢懈胁邪械屑 锌械褉械屑械薪薪褍褞 芯泻褉褍卸械薪懈褟

cfg = {
    'broker_ip': '192.168.137.1',
    'client_id': hexlify(machine.unique_id()),
    'mac': hexlify(WLAN().config('mac')),
    'last_message': 0,
    'message_interval': 5,
    'counter': 0,
    'wlan_ssid': 'P2797-24',  # 懈屑械薪邪 写谢懈薪薪褘械, 蟹邪褌芯 褌芯褔薪芯 胁褋械 锌芯薪褟褌薪芯
    'wlan_password': 'z0BcfpHu'
}

pins = {
    'red': machine.Pin(15, machine.Pin.OUT),
    'green': machine.Pin(12, machine.Pin.OUT),
    'blue': machine.Pin(13, machine.Pin.OUT),
    'STR': machine.Pin(15, machine.Pin.OUT),  # 褋懈褉械薪邪 薪邪 泻褉邪褋薪芯屑 锌懈薪械
    'LGT': machine.Pin(12, machine.Pin.OUT)  # 斜械谢褘泄 褋胁械褌 薪邪 蟹械谢械薪芯屑 锌懈薪械
}

topics = {
    'sub': b'RGB',
    'pub': b'RGBASK',
    'pub_id': b'RGBASK/' + cfg['mac'],
    'sub_id': b'RGB/' + cfg['mac']
}


