import time
import threading

class Sender:
	def __init__(self,sock,time_rate):
		print "Initaited"
		# Initiate Variables
		self.q = []
		self.rate = time_rate
		self.stop = False
		self.s = sock
		# Thread
		self.thread = threading.Thread(target=self.run, args=())
		self.thread.daemon = True
		self.thread.start()

	def run(self):
		print "Running"
		while True:
			if self.q:
				a = self.s.send(self.q.pop(0))
			# limit messages for no ban
			time.sleep(self.rate)

			if self.stop:
				return 0

	def stop_thread(self):
		print "Thread stopped"
		self.stop = True

	def add_queue(self,arr):
		for a in arr:
			self.q.append(a)

if __name__ == "__main__":
	pass
