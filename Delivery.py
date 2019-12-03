
import RPi.GPIO as GPIO
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
		global isReceipt
		isReceipt = True
		detectMode = False
		print("수령으로 처리되었습니다.")
		
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
		while True:
			response = input( '택배가 맞습니까? Y or N >>')
			if response == 'N'
				robbed = False
				response = 'Y'
				break
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