import RPi.GPIO as GPIO
from flask import Flask, render_template, request
app = Flask(__name__)
import picamera
import time
import pygame
import threading

GPIO.setmode(GPIO.BCM)
irpin = 21 # ���ܼ� ����
led = 20 # ǥ�õ�
Time = 0 # ������ Ÿ�Ӻ���
Mode = 0 # 0: �������� 1: �������� 2: ���� 3: ����
FirstDetect = False # ó�������� ǥ��

#- camera setting
camera = picamera.PiCamera()
camera.resolution = (800, 600)
#- mav setting
pygame.mixer.init()
beep = pygame.mixer.Sound("beep3.wav")

GPIO.setup(irpin, GPIO.IN)
GPIO.setup(led, GPIO.OUT)
GPIO.output(led, GPIO.LOW)

def Shot():
    now = time.localtime()
    fileName = "%04d-%02d-%02d %02d:%02d:%02d.jpg" % (now.tm_year, now.tm_mon, now.tm_mday,now.tm_hour, now.tm_min, now.tm_sec)
    camera.capture('picture/'+fileName)
    time.sleep(1)
    print("���� ����.")

class AsyncTask:
    def Detector(self):
        if x != 1:
            global Time
            Time += 1
            print(Time)
            if Time == 5:
                Mode = 1 # �����������
                Shot()
                print("������������ ��ȯ�Ǿ����ϴ�.")
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
    #app.run(host='0.0.0.0', port=80, debug=True)
    at = AsyncTask()
    try:
        while True:
            x = GPIO.input(irpin)
            time.sleep(0.1)
            if x != 1 : # ���� O
                if firstDetect == True and Mode == 0: # ó������
                    print("��ü�� �����Ǿ����ϴ�.")
                    at.Detector() # 10�� ī��Ʈ
                    firstDetect = False
                else:
                    GPIO.output(led, GPIO.HIGH)
            else: # ���� X
                if Mode == 1: # ������������϶� ����X == ����
                    Mode = 2 # ����
                    print("������ �����Ǿ����ϴ�..!")
                    at.Shot()
                    at.Alert()
                    Mode = 1 # �����������
                else:
                    GPIO.output(led, GPIO.LOW)
                    firstDetect = True

                        
    except KeyboardInterrupt:
        GPIO.output(led, GPIO.LOW)
        GPIO.cleanup()
        camera.close()



            
#- web ����
# type �ù谨����:detect/ ������� �۵�:detectM/ �����溸:alert/
# �ù����?:isBox / ��������?:isRobbed/���ɹ�ư :receipt
logs = {
'detect' : {'name' : '��ü�� �����Ǿ����ϴ�.', 'select' : False, 'time': '0-0-0'},
'detectM' : {'name' : '����������� �۵�', 'select' : False, 'time': '0-0-0'},
'alert' : {'name' : '������ �����Ǿ����ϴ�.', 'select' : False, 'time': '0-0-0'},
'isBox' : {'name' : '�ù�', 'select' : True, 'time': '0-0-0'},
'isRobbed' : {'name' : '����', 'select' : True, 'time': '0-0-0'},
'receipt' : {'name' : '����', 'select' : False, 'time': '0-0-0'}
}

@app.route("/<log>/<response>")
def action(log, response):
    global detectMode, robbed, isReceipt
    if log == 'isBox':
        if response == 'Y':
            detectMode = True
            message = "������������ ��ȯ�Ǿ����ϴ�."
            
    if log == 'isRobbed':
        if response == 'Y':
            robbed = True
            message = "�������� ó���Ǿ����ϴ�."
        else:
            robbed = False
            message = "�������� ó���Ǿ����ϴ�."
    if log == 'receipt':
        isReceipt = True
        detectMode = False
        message = "�������� ó���Ǿ����ϴ�."
        
    templateData = {
    'message' : message,
    'logs' : logs
    }
    return render_template('DropBox.html', **templateData)