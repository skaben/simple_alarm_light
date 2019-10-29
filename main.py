import machine
import time
import math
import ujson
import network

import urandom

quantNum = 50

pinD = dict()
pinD['STR'] = pinSTR
pinD['LGT'] = pinLGT

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

lenD =  dict()
lenD['STR'] = 0
lenD['LGT'] = 0
modeD = dict()
modeD['STR'] = ''
modeD['LGT'] = ''
onOff = dict()
onOff['STR'] = []
onOff['LGT'] = []
timePhase = dict()
timePhase['STR'] = []
timePhase['LGT'] = []
timeCurrent = dict()
timeCurrent['STR'] = 0
timeCurrent['LGT'] = 0
countCurrent = dict()
countCurrent['STR'] = 0
countCurrent['LGT'] = 0
timeSlice = dict()
timeSlice['STR'] = 0
timeSlice['LGT'] = 0

def randint(min, max):
  span = max - min + 1
  div = 0x3fffffff // span
  offset = urandom.getrandbits(30) // div
  val = min + offset
  return val
 
def parse_discr(chanName):
  global curCom, newCom, pinD
  global lenD, modeD, onOff, timePhase, timeCurrent, countCurrent, timeSlice
  if newCom[chanName] != curCom[chanName]:
    fields = newCom[chanName].split('/')
    if len(fields) < 2:
      if fields[0] == u'RESET':
        machine.reset()
        return
      else:
        return
    if (len(fields)-1)%2 != 0:
      return
    curCom[chanName] = newCom[chanName]
    modeD[chanName] = fields[len(fields)-1]
    lenD[chanName] = int(len(fields)/2)
    del onOff[chanName][:]
    del timePhase[chanName][:]
    i = 0
    while i < lenD[chanName]:
      onOff[chanName].append(fields[i*2])
      timePhase[chanName].append(fields[i*2+1])
      i = i + 1
    pinD[chanName].value(onOff[chanName][0])
    timeRandom = str(timePhase[chanName][0]).split('-')
    if len(timeRandom) != 2:
      timeS = int(timeRandom[0])
    else:
      timeS = int(randint(int(timeRandom[0]), int(timeRandom[1])))
    timeSlice[chanName] = timeS
    countCurrent[chanName] = 0
    timeCurrent[chanName] = time.ticks_ms()

def exec_discr(chanName):  
  global curCom, pinD
  global lenD, modeD, onOff, timePhase, timeCurrent, countCurrent, timeSlice
  if (time.ticks_ms() - timeCurrent[chanName]) >= timeSlice[chanName]:
    if modeD[chanName] == 'C':
      countCurrent[chanName] = (countCurrent[chanName] + 1) % lenD[chanName]
    elif modeD[chanName] == 'S':
      countCurrent[chanName] += 1
      if countCurrent[chanName] >= lenD[chanName]:
        lenD[chanName] = 0
        curCom[chanName] = ''
        return
    timeRandom = str(timePhase[chanName][countCurrent[chanName]]).split('-')
    if len(timeRandom) != 2:
      timeS = int(timeRandom[0])
    else:
      timeS = randint(int(timeRandom[0]), int(timeRandom[1]))
    timeSlice[chanName] = timeS
    pinD[chanName].value(int(onOff[chanName][countCurrent[chanName]]))
    timeCurrent[chanName] = time.ticks_ms()

def parse_command():
  global curCom, newCom
  global modeRGB,lenRGB,colorRGB,timeStaticRGB,timeChangeRGB,timeCurrentRGB,timeSliceRGB,curCom,rD,bD,gD
  global len, mode, onOff, timePhase, timeCurrent, countCurrent, timeSlice
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
    parse_discr('STR')
  if 'LGT' in newCom:
    parse_discr('LGT')
  
def sub_cb(topic, msg):
  global myMAC, topic_sub, topic_sub_id, newCom
  if topic == topic_sub or topic == topic_sub_id:
    try:
      newCom = ujson.loads(msg)
    except:
      time.sleep_ms(200)
      return
    parse_command()
    
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
  print ('Connect successfull')
except OSError as e:
  restart_and_reconnect()

while True:
  try:
    client.check_msg()
    if lenRGB > 0:
      if (time.ticks_ms() - timeCurrentRGB) >= timeSliceRGB:
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
        if timeChangeRGB[numBefore] > 0 and quantFlag == 0 :
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
    if lenD['STR'] > 0:
      exec_discr('STR')
    if lenD['LGT'] > 0:
      exec_discr('LGT')
  except OSError as e:
    machine.reset()

