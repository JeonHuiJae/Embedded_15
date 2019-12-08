import telepot
 
telegram_id = '1020899593' #아이디 입력
my_token = '868641147:AAGt-S98GEBY3PcKc7GmMty16RL7UhkUX4w' #token 입력
 
bot = telepot.Bot(my_token) #봇을 생성해줍니다.
 
msg = '텔레그램 메세지 테스트'
 
bot.sendMessage(chat_id = telegram_id, text = msg)