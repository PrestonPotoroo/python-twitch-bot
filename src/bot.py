import socket
import ssl
import signal
import sys
import re

# Custom modules
import config
from modules import Sender, Messages

s = None
sender = None

def signal_handler(sig, frame):
	print('You pressed Ctrl+C!')
	global s
	global sender
	if s:
		print "CLOSE"
		s.close()
	if sender:
		print "CLOSE THREAD"
		sender.stop_thread()
	sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

def run():
	global s
	global sender
	#CHAT_MSG = re.compile(r"^:\w+!\w+@\w+\.tmi\.twitch\.tv PRIVMSG #\w+ :")
	CHAT_MSG = re.compile(r"^:\w+!\w+@\w+\.tmi\.twitch\.tv PRIVMSG ")
	WHISPER_MSG = re.compile(r"^:\w+!\w+@\w+\.tmi\.twitch\.tv WHISPER \w+ :")

	try:
		context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
		s = context.wrap_socket(socket.socket(), server_hostname=config.HOST)
		s.connect((config.HOST,config.PORT))
		#s.send("CAP REQ :twitch.tv/membership twitch.tv/tags twitch.tv/commands\r\n")
		s.send("CAP REQ twitch.tv/commands\r\n")
		s.send("PASS "+config.PASS+"\r\n")
		s.send("NICK "+config.NICK+"\r\n")
		s.send("JOIN #"+config.CHANNEL+"\r\n")
		sender = Sender(s,config.RATE)
		connected = True
	except Exception as e:
		print str(e)
		connected = False

	msg_mngr = Messages(config.CHANNEL,config.VALID_USERS)
	send_list = []
	while connected:
		messages = []
		response = s.recv(1024).rstrip()
		#print response
		messages = response.split("\n")
		#i = 1
		for msg in messages:
			#print str(i)+". ",
			#print msg

			# get ping, send pong (keeps connection)
			if msg == "PING :tmi.twitch.tv":
				print "pong"
				s.send("PONG :tmi.twitch.tv\r\n")
			# get username, msg, channel (parses chat)
			elif CHAT_MSG.match(msg):
				user = re.search(r"\w+",msg).group()
				full_msg = CHAT_MSG.sub("",msg)
				full_msg = full_msg.split(":",1)
				channel = full_msg[0].strip()
				chat_msg = full_msg[1].strip()
				#print msg
				print channel + " " + user + ":" + chat_msg
				if msg_mngr.answer_key:
					send_list = msg_mngr.check_answers(chat_msg,user,channel)
				if chat_msg[0] == "!":
					send_list = msg_mngr.chat_cmds(chat_msg[1:],user,channel)
			# get username, msg (parses whispers)
			elif WHISPER_MSG.match(msg):
				user = re.search(r"\w+",msg).group()
				whisp_msg = WHISPER_MSG.sub("",msg)
				#print msg
				print "WHISPER - " + user + ":" + whisp_msg
				if whisp_msg[0] == "$":
					send_list = msg_mngr.whispers(whisp_msg[1:],user)
			else:
				print msg
			#i += 1

			# sends to queue in order for msg to be sent
			if send_list:
				sender.add_queue(send_list)
				send_list = []



if __name__ == "__main__":
	#run()
	#print config.HOST
	#print config.config.HOST
	pass
