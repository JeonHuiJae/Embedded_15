from flask import Flask, render_template, request
import picamera
import time
import pygame
import threading
import RPi.GPIO as GPIO
import json
import telepot
from telepot.loop import MessageLoop
import os
from subprocess import call
from datetime import datetime 

GPIO.setmode(GPIO.BCM)
irpin = 21 # 적외선 센서
led = 20 # 표시등
Time = 0 # 감지용 타임변수
Mode = 0 # 0: 감지상태 1: 도난방지 2: 도난 3: 수령
FirstDetect = False # 처음감지됨 표시ㅇㅇ
x = 0
fileNum = 0

curName = '00'
    
#- mav setting
pygame.mixer.init()
beep = pygame.mixer.Sound("beep3.wav")

GPIO.setup(irpin, GPIO.IN)
GPIO.setup(led, GPIO.OUT)
GPIO.output(led, GPIO.LOW)

app = Flask(__name__)

ip = "203.252.166.227"

def Send(Message):
    telegram_id = '-328726901' #아이디 입력
    my_token = '1016022560:AAEaEHoJxgyqpqm_vXpDCnE_TrZhKM3sMy4' #token 입력
    bot = telepot.Bot(my_token) #봇을 생성해줍니다.
    bot.sendMessage(chat_id = telegram_id, text = Message) #메시지를 보냅니다.

class AsyncTask:
    def Shot(self):
        camera = picamera.PiCamera()
        camera.resolution = (350, 400)
        camera.capture('static/ex1.jpg')
        time.sleep(0.1)
        camera.close()
        
    def Record(self):
        global curName
        camera2 = picamera.PiCamera()
        camera2.resolution= (350, 400)
        
        now = datetime.now()
        curName = now.strftime('%Y%m%d%H%M%S')
        
        camera2.start_recording('static/'+str(curName)+'.h264')
        camera2.wait_recording(5)
        camera2.stop_recording()
        camera2.close()

        print(curName)
        call("MP4Box -add static/"+str(curName)+".h264 static/"+str(curName)+".mp4", shell=True)
        print("인코딩 완료!!!")
        #return render_template("DropBox.html")

    def Detector(self):
        global Mode, ip, t3
        if x != 1:
            global Time
            Time += 1
            print(Time)
            if Time == 5:
                threading.Timer(1,at.Shot).start()  #사진 찍기
                print("물체가 감지되었습니다.")
                Send("* 물체가 감지되었습니다.\n* 택배가 맞으면 Yes, 아니면 No를 눌러주세요.\nhttp://"+ ip +"/detect")
                Time = 0
            else:
                threading.Timer(1,at.Detector).start()
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


@app.route("/detect")
def detect():
    message = "물체가 감지되었습니다.\n택배가 맞나요?"
    templateData = {
        'message' : message,
    }
    return render_template('DetectMode.html', **templateData)

@app.route("/message/<action>")
def action(action):
    global x, Mode, FirstDetect

    if action == "receive" :
        message = "수령처리되었습니다."
        Send("택배 수령이 완료되었습니다.")
        Mode = 0
        FirstDetect = False
    else :
        if x != 1 :
            message = "택배가 아닌 것으로 처리되었습니다."
            Send("택배가 아닌 것으로 처리되었습니다.")
            Mode = 0
            FirstDetect = False
        else :
            message = "그 사이에 물체가 사라졌습니다."
        
    templateData = {
        'message' : message,
    }    
    return render_template('Message.html', **templateData)

@app.route("/protect")
def protect():
    global Mode, ip
    if x != 1 :
        Mode = 1 # 도난방지모드
        print("도난방지모드로 전환되었습니다.")
        Send("* 택배를 보호중입니다.\n* 택배를 수령하기전에 수령을 눌러주세요.\nhttp://"+ ip +"/protect")
        message = "택배를 보호중입니다."
        templateData = {
            'message' : message,
        }
        return render_template('ProtectMode.html', **templateData)
    else :
        message = "그 사이에 물체가 사라졌습니다."
        templateData = {
            'message' : message,
        }
        return render_template('Message.html', **templateData)
            
@app.route("/robbed")
def robbed():
    global curName
    message = "도난이 감지되었습니다!!"
    templateData = {
        'curName' : curName,
        'message' : message,
    }
    return render_template('RobbedMode.html', **templateData)

@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response

if __name__ == '__main__':
    at = AsyncTask()
    try:
        threading.Timer(1,at.WebRun).start()
        while True:
            x = GPIO.input(irpin)
            time.sleep(0.1)
            if x != 1 : # 감지 O
                if FirstDetect == False and Mode == 0: # 처음감지
                    #print("물체가 감지되었습니다.")
                    at.Detector()
                    FirstDetect = True
                GPIO.output(led, GPIO.HIGH)
                    
            else: # 감지 X
                Time = 0
                if Mode == 1: # 도난방지모드일때 감지X == 도난
                    Mode = 2 # 도난
                    print("도난이 감지되었습니다!!!")
                    Send("!!!도난이 감지되었습니다!!!\nhttp://"+ ip +"/robbed")
                    threading.Timer(0,at.Record).start()
                    at.Alert()
                    Mode = 0 # 도난감지모드
                    FirstDetect = False
                GPIO.output(led, GPIO.LOW)
                FirstDetect = False

                        
    except KeyboardInterrupt:
        GPIO.output(led, GPIO.LOW)
        GPIO.cleanup()
        camera.close()


        