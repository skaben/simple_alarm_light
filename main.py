import machine
import time
import ujson
import network
import urandom

import config

"""
    запомнить и применять:

    - отступ в питоне - это 4 пробела. всегда.
    - глобалы не должны использоваться желательно никогда, потому что это 
    делает отладку программы очень сложной, а ее поведение - непредсказуемым.
    - не повторяться. есть что-то повторяющееся - сделай функцию.
"""

def randint(min, max):
    """ Микропитоний random.randint """
    span = max - min + 1
    div = 0x3fffffff // span
    offset = urandom.getrandbits(30) // div
    val = min + offset
    return val


def set_pwm():
    """ Для каждого цвета назначаем PWM по ключу с именем цвета """
    try:
        for color in config.pwm:
            config.pwm[color].duty(RGB[color])
    except:
        print('cannot set PWM, check config:\n{}'.format(config.pwm))
        return None


# упаковываем все, что имеет отношение к квантованию
QUANT = {
    'num': 20,
    'count': 0,
    'flag': 0
}

"""
    хранение текущего режима работы устройства

    curCom = dict()
    curCom['RGB'] = ''
    curCom['STR'] = ''
    curCom['LGT'] = ''
    
    проще записать так:  
"""

current_command = {
    'RGB': '',
    'STR': '',
    'LGT': ''
}

"""
    Я склонен к снейк_кейсу в названиях переменных и простых типов данных,
    а КэмелКейсом обычно называю классы.
"""

"""
    Вообще сюда прям просится нарисовать класс, поскольку атрибуты у STR и LGT
    полностью совпадают, и их можно было бы создавать одним конструктором,
    но не будем вводить лишние сущности и пока обойдемся тупо генерацией 
    словаря.
"""


def _hex(slice: str):
    return int(int(slice, 16) * 4)


def create_peripheral():
  """ Создаем словарь с ключами для устройства периферии
      Применяем принцип DRY - don't repeat yourself
      Кстати, в первой строке комментария кратко описано то, что делает функция
  """
  peripheral_dict =  {
                      'len': 0,
                      'mode': '',
                      'onoff': [],
                      'time': [],
                      'time_current': 0,
                      'time_slice': 0
                      }
  return peripheral_dict

# создаем по словарю для каждого устройства
LGT = create_peripheral()
STR = create_peripheral()
RGB = create_peripheral()

"""
    RGB у нас отличается, поэтому дополняем словарь RGB нужными полями, 
    передавая ему безымянный словарь через метод update
"""

RGB.update({
            'color': [],
            'count': 0,
            'last': 0,
            'red': 0,
            'green': 0,
            'blue': 0,
            'time_static': [],
            'time_change': [],
            'time_random': '',
})

# создаем функции для управления периферическими устройствами

def manage_rgb(payload):
    """ Управление устройством RGB """

    """
        Вот эту конструкцию вынесли в парсер:
         
        if 'RGB' in newCom:
            if newCom['RGB'] != curCom['RGB']:
                fields = newCom['RGB'].split('/')
                if len(fields) < 3:
                    if fields[0] == 'RESET':
                        machine.reset()
                return
            else:
                return
                
        Вот эту конструкцию не понял. Зачем она?
        
        if (len(fields)-1)%3 != 0:
            return
    """

    if len(payload) < 3:
        # todo: обработчик ошибок на случай кривого формата
        return

    current_command['RGB'] = payload # было curCom['RGB'] = newCom['RGB']

    """ обновляем конфигурацию устройства периферии.
    
        кстати, вот эти строчки 
                
        del colorRGB[:]
        del timeStaticRGB[:]
        del timeChangeRGB[:]
        
        Если уж есть такая задача, то list_name.del()
        но зачем удалять, если можно перезаписать?
    """

    # вот для таких вещей лучше использовать объекты и создать инстанс класса
    RGB.update({
        'mode': payload[-1],  # -1 это последний элемент списка
        'len': int(len(payload)/3),  # было lenRGB = int(len(fields)/3), чтоито?
        'color': [],
    })

    # обнуляем все списки для ключей, в которых встречается слово time
    for k in RGB:
        if 'time' in k:
            RGB[k] = []

    """
        теперь переписываем вот этот цикл:
        
        i = 0
        while i < lenRGB:
            colorRGB.append(fields[i*3])
            timeStaticRGB.append(fields[i*3+1])
            timeChangeRGB.append(int(fields[i*3+2]))
            i = i + 1  # лучше записать как i += 1
    """

    for i in range(RGB['len'] - 1):
        RGB['color'].append(payload[i * 3])
        RGB['time_static'].append(payload[i * 3 + 1])
        RGB['time_change'].append(payload[i * 3 + 2])

    """
    
        rD = int(colorRGB[0][0:2],16)*4
        gD = int(colorRGB[0][2:4],16)*4
        bD = int(colorRGB[0][4:6],16)*4
        
        redPWM.duty(rD)
        greenPWM.duty(gD)
        bluePWM.duty(bD)
        timeRandomRGB = str(timeStaticRGB[0]).split('-')

    """

    # DRY.
    RGB['red'] = _hex(RGB['color'][0][:2])
    RGB['green'] = _hex(RGB['color'][0][2:4])
    RGB['blue'] = _hex(RGB['color'][0][4:6])

    # запускаем пвмы вот такой конструкцией, благо ключи теперь совпадают
    [config.pwm[k].duty(RGB[k]) for k in RGB if k in ('red', 'green', 'blue')]

    RGB['time_random'] = str(RGB['time_static'][0]).split('-')

    """
        а зачем тут переменная timeSRGB?

        if len(timeRandomRGB) != 2:
            timeSRGB = int(timeRandomRGB[0])
        else:
            # вот эту конструкцию нужно дробить, нечитаемо
            timeSRGB = int(randint(int(timeRandomRGB[0]), int(timeRandomRGB[1])))
        timeSliceRGB = timeSRGB
    """

    if len(RGB['time_random']) != 2:
        RGB['time_slice'] = int(RGB['time_random'][0])
    else:
        (min, max) = RGB['time_random'][:2]
        RGB['time_slice'] = randint(int(min), int(max))

    """
       redPWM.duty(rD)
       greenPWM.duty(gD)
       bluePWM.duty(bD)
       timeRandomRGB = str(timeStaticRGB[0]).split('-') # aaaaaaaa
    """

    set_pwm() # устанавливаем PWM

    QUANT['count'] = 0
    QUANT['flag'] = 0
    RGB['time'] = time.ticks_ms()
    RGB['count'] = 0


def manage_lgt(payload):
    """ Управление устройством освещения """
    pass


def manage_str(payload):
    """ Управление устройством стробоскопа """
    pass


def parse_command(new_command):
    """ Парсер переданной команды """
    """
        создаем диспетчер, в котором каждому ключу соответствует функция
        обрати внимание, что имена функций здесь без вызова - это просто 
        ссылка на нее, без инициализации. Из известного мне - это наиболее 
        близкий аналог `case`, который можно создать средствами python.
    """
    dispatcher = {
        'LGT': manage_lgt,
        'STR': manage_str,
        'RGB': manage_rgb
    }
    # проверяем, есть ли в пришедшей команде данные по такому ключу
    for cmd in dispatcher:
        """
            метод get позволяет нам вернуть второй аргумент по умолчанию, 
            если в словаре нет такого ключа. без второго аргумента это выражение
            будет равнозначно `data = new_command.get(cmd, None)`
        """
        data = new_command.get(cmd) # то есть либо содержимое, либо None
        # затем проверяем, не тот же ли это конфиг, что уже у нас есть
        if data != current_command[cmd]:
            # парсим поля, чтобы не пропустить RESET - не повторяемся, опять же
            payload = data.split('/')
            # todo: обработчик ошибок на случай кривого формата
            if payload[0] == 'RESET':
                machine.reset()
            else:
                """
                    иначе вызываем функцию из диспетчера по ключу 
                    скажем, для 'RGB' это будет равнозначно manage_rgb(payload)
                    таким образом избавляемся от кучи нечитаемых if/else
                """
                dispatcher[cmd](payload)


def parse_command(newCom):
  global modeRGB,lenRGB,colorRGB,timeStaticRGB,timeChangeRGB,timeCurrentRGB,timeSliceRGB,curCom,rD,bD,gD
  global lenSTR, modeSTR,onOffSTR,timeCurrentSTR,countCurrentSTR,timeSliceSTR
  global lenLGT, modeLGT,onOffLGT,timeCurrentLGT,countCurrentLGT,timeSliceLGT
  if 'RGB' in newCom:
    if newCom['RGB'] != curCom['RGB']:
      fields = newCom['RGB'].split('/')
      if len(fields) < 3:
        if fields[0] == 'RESET':
          machine.reset()
          return
        else:
          return
      if (len(fields)-1)%3 != 0:
        return
      curCom['RGB'] = newCom['RGB']
      modeRGB = fields[len(fields)-1]
      lenRGB = int(len(fields)/3)
      del colorRGB[:]
      del timeStaticRGB[:]
      del timeChangeRGB[:]
      i = 0
      while i < lenRGB:
        colorRGB.append(fields[i*3])
        timeStaticRGB.append(fields[i*3+1])
        timeChangeRGB.append(int(fields[i*3+2]))
        i = i + 1
      rD = int(colorRGB[0][0:2],16)*4
      gD = int(colorRGB[0][2:4],16)*4
      bD = int(colorRGB[0][4:6],16)*4
      redPWM.duty(rD)
      greenPWM.duty(gD)
      bluePWM.duty(bD)
      timeRandomRGB = str(timeStaticRGB[0]).split('-')
      if len(timeRandomRGB) != 2:
        timeSRGB = int(timeRandomRGB[0])
      else:
        timeSRGB = int(randint(int(timeRandomRGB[0]), int(timeRandomRGB[1])))
      timeSliceRGB = timeSRGB
      countCurrentRGB = 0
      quantCount = 0
      quantFlag = 0
      timeCurrentRGB = time.ticks_ms()
  if 'STR' in newCom:
    if newCom['STR'] != curCom['STR']:
      fields = newCom['STR'].split('/')
      if len(fields) < 2:
        if fields[0] == u'RESET':
          machine.reset()
          return
        else:
          return
      if (len(fields)-1)%2 != 0:
        return
      curCom['STR'] = newCom['STR']
      modeSTR = fields[len(fields)-1]
      lenSTR = int(len(fields)/2)
      del onOffSTR[:]
      del timeSTR[:]
      i = 0
      while i < lenSTR:
        onOffSTR.append(fields[i*2])
        timeSTR.append(fields[i*2+1])
        i = i + 1
      pinSTR.value(onOffSTR[0])
      timeRandomSTR = str(timeSTR[0]).split('-')
      if len(timeRandomSTR) != 2:
        timeS = int(timeRandomSTR[0])
      else:
        timeS = int(randint(int(timeRandomSTR[0]), int(timeRandomSTR[1])))
      timeSliceSTR = timeS
      countCurrentSTR = 0
      timeCurrentSTR = time.ticks_ms()
  if 'LGT' in newCom:
    if newCom['LGT'] != curCom['LGT']:
      fields = newCom['LGT'].split('/')
      if len(fields) < 2:
        if fields[0] == u'RESET':
          machine.reset()
          return
        else:
          return
      if (len(fields)-1)%2 != 0:
        return
      curCom['LGT'] = newCom['LGT']
      modeLGT = fields[len(fields)-1]
      lenLGT = int(len(fields)/2)
      del onOffLGT[:]
      del timeLGT[:]
      i = 0
      while i < lenLGT:
        onOffLGT.append(fields[i*2])
        timeLGT.append(fields[i*2+1])
        i = i + 1
      pinLGT.value(onOffLGT[0])
      timeRandomLGT = str(timeLGT[0]).split('-')
      if len(timeRandomLGT) != 2:
        timeSL = int(timeRandomLGT[0])
      else:
        timeSL = int(randint(int(timeRandomLGT[0]), int(timeRandomLGT[1])))
      timeSliceLGT = timeSL
      countCurrentLGT = 0
      timeCurrentLGT = time.ticks_ms()

"""
def sub_cb(topic, msg):
  global newCom, myMAC, topic_sub, topic_sub_id
  if topic == topic_sub or topic == topic_sub_id:
    try:
      newCom = ujson.loads(msg)
    except:
      time.sleep_ms(200)
      return
    parse_command(newCom)
"""

def mqtt_callback(topic, msg):
    """ Callback function for topic parsing """
    if topic in (config.topics['sub'], config.topics['sub_id']):
        try:
            command = ujson.loads(msg)
            return parse_command(command)
        except:
            time.sleep(.2)
            return

"""
def connect_and_subscribe():
  global client_id, mqtt_server, topic_sub, myMAC
  global redPWM, greenPWM, bluePWM
  client = MQTTClient(client_id, mqtt_server)
  client.set_callback(sub_cb)
  client.connect()
  client.subscribe(topic_sub)
  client.subscribe(topic_sub_id)
  print('Connected to %s MQTT broker, subscribed to %s topic' % (mqtt_server, topic_sub))
  print('Connected to %s MQTT broker, subscribed to %s topic' % (mqtt_server, topic_sub_id))
  greenPin.value(0)  
  ## Не забыть раскомментировать три следующих строки перед реальным использвоанием!!!
  #redPWM = machine.PWM(redPin, freq=1000)
  #greenPWM = machine.PWM(greenPin, freq=1000)
  #bluePWM = machine.PWM(bluePin, freq=1000)
  client.publish(topic_pub+'/'+myMAC, 'CUP/{"lts":"'+str(time.ticks_ms())+'"}')
  return client
"""


def connect_and_subscribe():
    """ Соединение с брокером и подписка на топики """
    server = config.cfg.get('broker_ip')
    client = MQTTClient(config.cfg.get('client_id'), server)
    client.set_callback(mqtt_callback)
    client.connect()
    sub_topics = [t for t in config.topics if 'sub' in t]
    client.subscribe(sub_topics)
    print('connected to {}, subscribed to {}'.format(server, sub_topics))
    config.pins['green'].value(0)
    cmd = 'CUP/{"lts":"{}"}'.format(time.ticks_ms())
    client.publish(config.topics['pub_id'], cmd)
    return client


def restart_and_reconnect():
    """ Рестарт и повторное соединение с брокером """
    signal_pin = config.pins.get('green')
    print('Failed to connect to MQTT broker. Reconnecting...')
    for x in range(10):
        signal_pin.value(0)
        time.sleep(.25)
        signal_pin.value(1)
        time.sleep(.25)
    machine.reset()


def main():
    """ Основная функция приложения """
    try:
        client = connect_and_subscribe()
    except OSError as e:
        print(e)
        restart_and_reconnect()

    while True:
        client.check_msg()
        # вот такую логику лучше разбивать на функции или на методы.
        # потому что в пачке ифов разбираться очень затруднительно, тем более
        # тестировать их потом.
        if RGB.get('len') > 0:
            """     
                # Смена цвета
                if modeRGB == 'C' and quantFlag == 0:
                    numBefore = countCurrentRGB
                    countCurrentRGB = (countCurrentRGB + 1) % lenRGB
                elif modeRGB == 'S' and quantFlag == 0:
                    numBefore = countCurrentRGB
                    countCurrentRGB += 1
                    if countCurrentRGB >= lenRGB:
                        lenRGB = 0
                        curCom['RGB'] = ''
                        continue
            """

            if (time.ticks_ms() - RGB['time_current']) >= RGB['time_slice']:
                before = RGB['count']
                # DRY. DRY. DRY.
                if QUANT['flag'] == 0:
                    if RGB['mode'] == 'C':
                        RGB['count'] = (before + 1) % RGB['len']
                    elif RGB['mode'] == 'S':
                        RGB['count'] += 1
                        if RGB['count'] >= RGB['len']:
                            RGB['len'] = 0
                            continue
                    try:
                        """
                            timeSliceRGB = int(timeChangeRGB[numBefore]/quantNum)
                        """
                        tc = RGB.get('time_change')[before]
                        if tc > 0:
                            RGB['time_slice'] = int(tc/QUANT['num'])
                    except IndexError:
                        print('index error in RGB conf')
                if QUANT['flag'] == 1:


            # И вот где то тут я закончился)))


def manage_pwm_delta(prev_idx):
    """ # Плавное изменение цвета"""

    """
          rDDelta = int((int(colorRGB[countCurrentRGB][0:2],16)*4 - int(colorRGB[numBefore][0:2],16)*4)/quantNum)
          gDDelta = int((int(colorRGB[countCurrentRGB][2:4],16)*4 - int(colorRGB[numBefore][2:4],16)*4)/quantNum)
          bDDelta = int((int(colorRGB[countCurrentRGB][4:6],16)*4 - int(colorRGB[numBefore][4:6],16)*4)/quantNum)
          quantFlag = 1
          quantCount = 1
          rD += rDDelta
          gD += gDDelta
          bD += bDDelta
    """

    delta = dict()

    idx = RGB['count']
    color_now = RGB['color'][idx]
    color_prev = RGB['color'][prev_idx]

    def _pwm_calc(rng):
        return _hex(color_now[rng]) - _hex(color_prev[rng]) / QUANT['num']

    delta['red'] = _pwm_calc(slice(0, 2))
    delta['green'] = _pwm_calc(slice(2, 4))
    delta['blue'] = _pwm_calc(slice(4, 6))

    QUANT['flag'] = 1
    QUANT['count'] = 1

    for key in delta:
        RGB[key] += delta[key]

  try:
    client.check_msg()
    if lenRGB > 0:
      if (time.ticks_ms() - timeCurrentRGB) >= timeSliceRGB:
        # Смена цвета
        if modeRGB == 'C' and quantFlag == 0:
          numBefore = countCurrentRGB
          countCurrentRGB = (countCurrentRGB + 1) % lenRGB
        elif modeRGB == 'S' and quantFlag == 0:
          numBefore = countCurrentRGB
          countCurrentRGB += 1
          if countCurrentRGB >= lenRGB:
            lenRGB = 0
            curCom['RGB'] = ''
            continue
        # И вот где-то тут я закончился)
        if timeChangeRGB[numBefore] > 0 and quantFlag == 0:
            timeSliceRGB = int(timeChangeRGB[numBefore] / quantNum)
            rDDelta = int((int(colorRGB[countCurrentRGB][0:2], 16) * 4 - int(
                colorRGB[numBefore][0:2], 16) * 4) / quantNum)
            gDDelta = int((int(colorRGB[countCurrentRGB][2:4], 16) * 4 - int(
                colorRGB[numBefore][2:4], 16) * 4) / quantNum)
            bDDelta = int((int(colorRGB[countCurrentRGB][4:6], 16) * 4 - int(
                colorRGB[numBefore][4:6], 16) * 4) / quantNum)
            quantFlag = 1
            quantCount = 1
            rD += rDDelta
            gD += gDDelta
            bD += bDDelta
        elif quantFlag == 1 and quantCount < quantNum:
          timeSliceRGB = int(timeChangeRGB[numBefore]/quantNum)
          quantCount += 1
          rD += rDDelta
          gD += gDDelta
          bD += bDDelta
        else:
          quantFlag = 0
          quantCount = 0
          rD = int(colorRGB[countCurrentRGB][0:2],16)*4
          gD = int(colorRGB[countCurrentRGB][2:4],16)*4
          bD = int(colorRGB[countCurrentRGB][4:6],16)*4
          timeRandomRGB = str(timeStaticRGB[countCurrentRGB]).split('-')
          print(timeRandomRGB)
          if len(timeRandomRGB) != 2:
            timeSRGB = int(timeRandomRGB[0])
          else:
            timeSRGB = randint(int(timeRandomRGB[0]), int(timeRandomRGB[1]))
          timeSliceRGB = timeSRGB
        redPWM.duty(rD)
        greenPWM.duty(gD)
        bluePWM.duty(bD)
        timeCurrentRGB = time.ticks_ms()
    if lenSTR > 0:
      if (time.ticks_ms() - timeCurrentSTR) >= timeSliceSTR:
        # Смена такта
        if modeSTR == 'C':
          countCurrentSTR = (countCurrentSTR + 1) % lenSTR
        elif modeSTR == 'S':
          countCurrentSTR += 1
          if countCurrentSTR >= lenSTR:
            lenSTR = 0
            curCom['STR'] = ''
            continue
        timeRandomSTR = str(timeSTR[countCurrentSTR]).split('-')
        if len(timeRandomSTR) != 2:
          timeS = int(timeRandomSTR[0])
        else:
          timeS = randint(int(timeRandomSTR[0]), int(timeRandomSTR[1]))
        timeSliceSTR = timeS
        pinSTR.value(int(onOffSTR[countCurrentSTR]))
        timeCurrentSTR = time.ticks_ms()
    if lenLGT > 0:
      if (time.ticks_ms() - timeCurrentLGT) >= timeSliceLGT:
        # Смена такта
        if modeLGT == 'C':
          countCurrentLGT = (countCurrentLGT + 1) % lenLGT
        elif modeLGT == 'S':
          countCurrentLGT += 1
          if countCurrentLGT >= lenLGT:
            lenLGT = 0
            curCom['LGT'] = ''
            continue
        timeRandomLGT = str(timeLGT[countCurrentLGT]).split('-')
        if len(timeRandomLGT) != 2:
          timeSL = int(timeRandomLGT[0])
        else:
          timeSL = randint(int(timeRandomLGT[0]), int(timeRandomLGT[1]))
        timeSliceLGT = timeSL
        pinLGT.value(int(onOffLGT[countCurrentLGT]))
        timeCurrentLGT = time.ticks_ms()
      
  except OSError as e:
    restart_and_reconnect()


