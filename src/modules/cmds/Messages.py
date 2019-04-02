import random

class Messages():
	def __init__(self,default_chan,valid_users):
		self.channels = [default_chan]
		self.curr_channel = default_chan
		self.valid_users = valid_users
		self.answer_key = {}

		# In Development for making an easier way to create commands
		self.cmd_list = { "join": {"action":["PART","JOIN"],"args":2},
			"part": {"action":["PART"],"args":2},
			"onlyjoin": {"action":["JOIN"],"args":2},
			"pog": {"action":["PRIVMSG"],"args":1,"msg":"PogChamp","limit":1},
			"curr": {"action":["PRIVMSG"],"args":1,"msg":"Current Channel: %currchan%","limit":1},
			"channels": {"action":["PRIVMSG"],"args":1,"msg":"Channel List [%chanlist%]","limit":1}
		}

		self.sub_vars = {"%currchan%":self.get_currchan,"%chanlist%":self.get_channels}

	def get_currchan(self):
		return self.curr_channel
	def get_channels(self):
		return ", ".join(self.channels)

	# Whisper Commands Execution: PART,JOIN,PRIVMSG only
	def whispers(self,cmd,user):
		raw_data = cmd.split()
		cmd = raw_data[0]
		if len(raw_data) > 1:
			args = raw_data[1:]

		send_list = []
		if user not in self.valid_users:
			return send_list

		if cmd in self.cmd_list:
			if self.cmd_list[cmd]["args"] != len(raw_data):
				return send_list
			for action in self.cmd_list[cmd]["action"]:
				if action == "PART":
					chan = args[0]
					if chan in self.channels:
						self.channels.remove(chan)
						# Needed when parting a channel then joining a channel right after
						if "JOIN" in self.cmd_list[cmd]["action"]:
							chan = self.curr_channel
						else:
							if len(self.channels):
								self.curr_channel = self.channels[-1]
							else:
								self.curr_channel = ""
						send_list.append("PART " + chan + "\r\n")
					if chan in self.answer_key:
						del self.answer_key[chan]
				elif action == "JOIN":
					chan = args[0]
					self.curr_channel = chan
					send_list.append("JOIN #" + self.curr_channel + "\r\n")
					self.channels.append(self.curr_channel)
				elif action == "PRIVMSG":
					if not self.curr_channel:
						return send_list
					msg = self.cmd_list[cmd]["msg"]
					if msg:
						for k,v in self.sub_vars.iteritems():
							msg = msg.replace(k,v())
					else:
						msg = args[1]
					# for spamming
					for i in xrange(self.cmd_list[cmd]["limit"]):
						send_list.append("PRIVMSG #" + self.curr_channel + " :/w "+user+" "+msg+"\r\n")
						if not (i % 2):
							msg += " ."
						else:
							msg = msg[:-2]
		print send_list
		return send_list

	# Regular Chat Commands
	def chat_cmds(self,chat_msg,user,chan):
		words = chat_msg.split()
		send_list = []

		if words[0] == "math" and len(words) == 1:
			if chan in self.answer_key and "math" in self.answer_key[chan]:
				send_list.append("PRIVMSG " + chan + " : "+self.answer_key[chan]["math"][0]+"\r\n")
				return send_list
			a = random.randint(101,999)
			b = random.randint(2,9)
			send_list.append("PRIVMSG " + chan + " : "+str(a)+"*"+str(b)+"\r\n")
			self.answer_key[chan] = {"math":(str(a)+"*"+str(b),str(a*b))}
		return send_list

	# Checking answers for regular chat cmds
	def check_answers(self,chat_msg,user,chan):
		words = chat_msg.strip()
		send_list = []
		if chan in self.answer_key and "math" in self.answer_key[chan]:
			if words == self.answer_key[chan]["math"][1]:
				send_list.append("PRIVMSG " + chan + " : Congratulations  "+user+" for the correct answer!\r\n")
				del self.answer_key[chan]["math"]
				print self.answer_key
		return send_list
