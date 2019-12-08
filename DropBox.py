from flask import Flask, render_template, request
import picamera
import time
import pygame
import threading
import RPi.GPIO as GPIO
import json
GPIO.setmode(GPIO.BCM)
irpin = 21 # 적외선 센서
led = 20 # 표시등
Time = 0 # 감지용 타임변수
Mode = 0 # 0: 감지상태 1: 도난방지 2: 도난 3: 수령
FirstDetect = False # 처음감지됨 표시ㅇㅇ

#- mav setting
pygame.mixer.init()
beep = pygame.mixer.Sound("beep3.wav")

GPIO.setup(irpin, GPIO.IN)
GPIO.setup(led, GPIO.OUT)
GPIO.output(led, GPIO.LOW)

app = Flask(__name__)



class AsyncTask:
    def Shot(self):
        camera = picamera.PiCamera()
        camera.resolution = (800, 600)
        camera.capture('picture/ex1.jpg')
        time.sleep(0.1)
        camera.close()

        #return render_template("DropBox.html")

    def Detector(self):
        global Mode
        if x != 1:
            global Time
            Time += 1
            print(Time)
            if Time == 5:
                Mode = 1 # 도난방지모드
                threading.Timer(1,self.Shot).start()
                print("도난방지모드로 전환되었습니다.")
                Time = 0
            else:
                threading.Timer(1,self.Detector).start()
        else:
            Time =0
            Mode = 0

    def Alert(self):
        global respond, robbed, Time
        Time = 0;
        beep.play()
        while True:
            Time += 1
            time.sleep(0.2)
            GPIO.output(led, GPIO.HIGH)
            time.sleep(0.2)
            GPIO.output(led, GPIO.LOW)
            time.sleep(0.2)
            if Time == 8:
                Time = 0
                break
                
    def WebRun(self):
        global app
        app.run(host='0.0.0.0', port=80, debug=False, threaded=True)


@app.route("/")
def page():
    message = "환영합니다."
    templateData = {
        'message' : message,
    }
    return render_template('DropBox.html', **templateData)

if __name__ == '__main__':
    at = AsyncTask()
    try:
        threading.Timer(1,at.WebRun).start()
        while True:
            x = GPIO.input(irpin)
            time.sleep(0.1)
            if x != 1 : # 감지 O
                if FirstDetect == False and Mode == 0: # 처음감지
                    print("물체가 감지되었습니다.")
                    at.Detector() # 10초 카운트
                    FirstDetect = True
                GPIO.output(led, GPIO.HIGH)
                    
            else: # 감지 X
                Time = 0
                if Mode == 1: # 도난방지모드일때 감지X == 도난
                    Mode = 2 # 도난
                    print("도난이 감지되었습니다..!")
                    threading.Timer(1,at.Shot).start()
                    at.Alert()
                    Mode = 0 # 도난감지모드
                GPIO.output(led, GPIO.LOW)
                FirstDetect = False

                        
    except KeyboardInterrupt:
        GPIO.output(led, GPIO.LOW)
        GPIO.cleanup()
        camera.close()



            
#- web 제어
# type 택배감지됨:detect/ 감지모드 작동:detectM/ 도난경보:alert/
# 택배맞음?:isBox / 도난맞음?:isRobbed/수령버튼 :receipt

@app.route("/<page>")
def action(page):
    global detectMode, robbed, isReceipt
    if page == 'isRight':
        if response == 'Y':
            detectMode = True
            message = "택배가 맞나요?"
            
    if page == 'Anti-theft':
            message = "도난방지모드 입니다"
    if page == 'Robbed':
        message = "도난이 감지되었습니다"
        
    templateData = {
        'message' : message,
    }
    return render_template('DropBox.html', **templateData)