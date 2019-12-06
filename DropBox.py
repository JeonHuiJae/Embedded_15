from flask import Flask, render_template, request
import picamera
import time
import pygame
import threading
import RPi.GPIO as GPIO
import json
app = Flask(__name__)

GPIO.setmode(GPIO.BCM)
irpin = 21 # 적외선 센서
led = 20 # 표시등
Time = 0 # 감지용 타임변수
Mode = 0 # 0: 감지상태 1: 도난방지 2: 도난 3: 수령
FirstDetect = False # 처음감지됨 표시
logs = {
'detect' : {'name' : '물체가 감지되었습니다.', 'select' : False, 'time': '0-0-0'}
}

#- camera setting
camera = picamera.PiCamera()
camera.resolution = (800, 600)
#- mav setting
pygame.mixer.init()
beep = pygame.mixer.Sound("beep3.wav")

GPIO.setup(irpin, GPIO.IN)
GPIO.setup(led, GPIO.OUT)
GPIO.output(led, GPIO.LOW)

def loadJson():
    global logs
    with open('logData.json', 'r') as f:
        logs = json.load(f)

def Shot():
    now = time.localtime()
    fileName = "%04d-%02d-%02d %02d:%02d:%02d.jpg" % (now.tm_year, now.tm_mon, now.tm_mday,now.tm_hour, now.tm_min, now.tm_sec)
    with picamera.PiCamera() as camera:
        camera.capture('picture/'+fileName)
    time.sleep(1)
    print("사진 저장.")

class AsyncTask:
    
    def Detector(self):
        global Mode
        if x != 1:
            global Time
            Time += 1
            print(Time)
            if Time == 5:
                Mode = 1 # 도난방지모드
                Shot()
                print("도난방지모드로 전환되었습니다.")
                Time = 0
            else:
                threading.Timer(1,self.Detector).start()
        else:
            Time =0

    def Alert(self):
        global respond, robbed, Time
        while True:
            Time += 1
            beep.play()
            time.sleep(1.0)
            GPIO.output(led, GPIO.HIGH)
            time.sleep(1)
            GPIO.output(led, GPIO.LOW)
            time.sleep(1)
            if Time == 3:
                Time = 0
                break

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True, threaded=True)
    at = AsyncTask()
    try:
        while True:
            x = GPIO.input(irpin)
            time.sleep(0.1)
            if x != 1 : # 감지 O
                if firstDetect == True and Mode == 0: # 처음감지
                    print("물체가 감지되었습니다.")
                    at.Detector() # 10초 카운트
                    firstDetect = False
                else:
                    GPIO.output(led, GPIO.HIGH)
            else: # 감지 X
                Time = 0
                if Mode == 1: # 도난방지모드일때 감지X == 도난
                    Mode = 2 # 도난
                    print("도난이 감지되었습니다..!")
                    Shot()
                    at.Alert()
                    Mode = 0 # 도난감지모드
                else:
                    GPIO.output(led, GPIO.LOW)
                    firstDetect = True

                        
    except KeyboardInterrupt:
        GPIO.output(led, GPIO.LOW)
        GPIO.cleanup()
        camera.close()



            
#- web 제어
# type 택배감지됨:detect/ 감지모드 작동:detectM/ 도난경보:alert/
# 택배맞음?:isBox / 도난맞음?:isRobbed/수령버튼 :receipt

@app.route("/")
def page():
    message = "환영합니다."
    templateData = {
        'message' : message,
        'logs' : logs
    }
    return render_template('DropBox.html', **templateData)

@app.route("/<log>/<response>")
def action(log, response):
    global detectMode, robbed, isReceipt
    if log == 'isBox':
        if response == 'Y':
            detectMode = True
            message = "도난방지모드로 전환되었습니다."
            
    if log == 'isRobbed':
        if response == 'Y':
            robbed = True
            message = "도난으로 처리되었습니다."
        else:
            robbed = False
            message = "오감지로 처리되었습니다."
    if log == 'receipt':
        isReceipt = True
        detectMode = False
        message = "수령으로 처리되었습니다."
        
    templateData = {
        'message' : message,
        'logs' : logs
    }
    return render_template('DropBox.html', **templateData)