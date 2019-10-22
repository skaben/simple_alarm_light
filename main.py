import machine
import time
import math
import ujson
import network

import urandom

quantNum = 20

newCom = dict()
curCom = dict()
curCom['RGB'] = ''
curCom['STR'] = ''
curCom['LGT'] = ''
modeRGB = ''
lenRGB = 0
timeCurrentRGB = 0
countCurrentRGB = 0
colorRGB = []
timeStaticRGB = []
timeChangeRGB = []
timeSliceRGB = 0
quantCount = 0
quantFlag = 0
rD = 0
bD = 0
gD = 0
lastRGB = 0

lenSTR = 0
modeSTR = ''
onOffSTR = []
timeCurrentSTR = 0
countCurrentSTR = 0
timeSliceSTR = 0
timeSTR = []

lenLGT = 0
modeLGT = ''
onOffLGT = []
timeCurrentLGT = 0
countCurrentLGT = 0
timeSliceLGT = 0
timeLGT = []

def randint(min, max):
    span = max - min + 1
    div = 0x3fffffff // span
    offset = urandom.getrandbits(30) // div
    val = min + offset
    return val

def parse_command(newCom):
  global modeRGB,lenRGB,colorRGB,timeStaticRGB,timeChangeRGB,timeCurrentRGB,timeSliceRGB,curCom,rD,bD,gD
  global lenSTR, modeSTR,onOffSTR,timeCurrentSTR,countCurrentSTR,timeSliceSTR
  global lenLGT, modeLGT,onOffLGT,timeCurrentLGT,countCurrentLGT,timeSliceLGT
  if 'RGB' in newCom:
    if newCom['RGB'] != curCom['RGB']:
      fields = newCom['RGB'].split('/')
      if len(fields) < 3:
        if fields[0] == u'RESET':
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

def sub_cb(topic, msg):
  global newCom, myMAC, topic_sub, topic_sub_id
  if topic == topic_sub or topic == topic_sub_id:
    try:
      newCom = ujson.loads(msg)
    except:
      time.sleep_ms(200)
      return
    parse_command(newCom)
    
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

def restart_and_reconnect():
  print('Failed to connect to MQTT broker. Reconnecting...')
  for x in range(10):
    greenPin.value(1)
    time.sleep_ms(250)
    greenPin.value(0)
    time.sleep_ms(250)
  machine.reset()

try:
  client = connect_and_subscribe()
except OSError as e:
  restart_and_reconnect()

while True:
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
            continue
        if timeChangeRGB[numBefore] > 0 and quantFlag == 0 :
          # Плавное изменение цвета
          timeSliceRGB = int(timeChangeRGB[numBefore]/quantNum)
          rDDelta = int((int(colorRGB[countCurrentRGB][0:2],16)*4 - int(colorRGB[numBefore][0:2],16)*4)/quantNum)
          gDDelta = int((int(colorRGB[countCurrentRGB][2:4],16)*4 - int(colorRGB[numBefore][2:4],16)*4)/quantNum)
          bDDelta = int((int(colorRGB[countCurrentRGB][4:6],16)*4 - int(colorRGB[numBefore][4:6],16)*4)/quantNum)
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


