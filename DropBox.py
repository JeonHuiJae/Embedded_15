
import RPi.GPIO as GPIO
from flask import Flask, render_template, request
app = Flask(__name__)
import picamera
import time
import pygame

GPIO.setmode(GPIO.BCM)
irpin = 21 # 적외선 센서
led = 20 # 표시등
Time = 0 # 감지용 타임변수
firstDetect = False # 처음감지됨 표시
detectMode = False # 도난방지모드
isReceipt = False
robbed = False # 도난감지
response = 'Y' # 사용자 입력

#- camera setting
camera = picamera.PiCamera()
camera.resolution = (800, 600)
#- mav setting
pygame.mixer.init()
beep = pygame.mixer.Sound("beep.wav")
#- LED setting
GPIO.setup(irpin, GPIO.IN)
GPIO.setup(led, GPIO.OUT)
GPIO.output(led, GPIO.LOW)

if __name__ == '__main__':
	#app.run(host='0.0.0.0', port=80, debug=True)
	try:
		while True:
			x = GPIO.input(irpin)
			time.sleep(0.1)
			if x != 1 : # 감지 O
				if isReceipt == False:
					if firstDetect == False: # 처음감지
						print("물체가 감지되었습니다.")
						Detector() # 10초 카운트
						firstDetect = True
					GPIO.output(led, GPIO.HIGH)
			else: # 감지 X
				if detectMode == True: # 도난방지모드일때 감지X == 도난
					robbed = True
					print("도난이 감지되었습니다..!")
					Shot()
					Alert()
					while True:
						response = input( '도난이 맞습니까? Y or N >>')
						if response == 'N'
							robbed = False
							response = 'Y'
							break
				else:
					if isReceipt == True:
						isReceipt = False
					else:
						GPIO.output(led, GPIO.LOW)
						firstDetect = False
			
			
	except KeyboardInterrupt:
		GPIO.output(led, GPIO.LOW)
		GPIO.cleanup()
		camera.close()

def Detector(self):
	global Time
	Time += 1
	print(Time)
	if Time == 10:
		detectMode = True
		Shot()
		print("도난방지모드로 전환되었습니다.")
		Time = 0
	else:
		threading.Timer(1,self.Detector).start()

def Shot():
	now = time.localtime()
	fileName = "%04d-%02d-%02d %02d:%02d:%02d" % (now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec)
	camera.capture('picture/'+fileName)
	time.sleep(1)
	print("사진 저장.")
	
def Alert(self):
	global respond, robbed
	whie True:
		beep.play()
		time.sleep(1.0)
		
		GPIO.output(led, GPIO.HIGH)
		time.sleep(1)
		GPIO.output(led, GPIO.LOW)
		time.sleep(1)
		
		if response != 'N'
			hreading.Timer(1,self.Alert).start()
			
			
			
#- web 제어
# type 택배감지됨:detect/ 감지모드 작동:detectM/ 도난경보:alert/
# 택배맞음?:isBox / 도난맞음?:isRobbed/수령버튼 :receipt
logs = {
'detect' : {'name' : '물체가 감지되었습니다.', 'select' : False, 'time': '0-0-0'},
'detectM' : {'name' : '도난방지모드 작동', 'select' : False, 'time': '0-0-0'},
'alert' : {'name' : '도난이 감지되었습니다.', 'select' : False, 'time': '0-0-0'},
'isBox' : {'name' : '택배', 'select' : True, 'time': '0-0-0'},
'isRobbed' : {'name' : '도난', 'select' : True, 'time': '0-0-0'},
'receipt' : {'name' : '수령', 'select' : False, 'time': '0-0-0'}
}

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
		else
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
