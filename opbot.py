import socket
import time
import logging
import logging.handlers

class OpBot:

	def __init__(self):
		self.nick = "BotNick"
		self.server = "Server"
		self.port = 6667
		self.channel = "#channel"
		self.init_socket()
		self.whitelist = ["nick1", "nick2"]
		# Setup logging
		logging.basicConfig(filename="log.txt", level=logging.INFO, 
			format='%(asctime)s %(message)s', datefmt='[%H:%M:%S] %p')
		self.logger = logging.getLogger(__name__)
		handler = logging.handlers.RotatingFileHandler("log.txt", maxBytes=10485760)
		self.logger.addHandler(handler)
	
	def init_socket(self):
		self.ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.ircsock.settimeout(4*60) # 4 min

	def execute(self):
		self.connect()
		# Main loop 
		while 1:
			try:
			  	ircmsg = self.ircsock.recv(2048) 
			  	ircmsg = ircmsg.strip('\n\r')
				self.logger.info(ircmsg) 
				self.activities(ircmsg)
			except socket.timeout:
				self.logger.warning("Timeout error")
				self.connect()

	def connect(self):
		self.ircsock.close()
		self.init_socket()
		try:
			# Connect to irc server
			self.logger.info("Connecting to server " + self.server)
			self.ircsock.connect((self.server, self.port))
			self.ircsock.send("USER " + self.nick + " 0 * : " + self.nick + "\r\n")
			self.ircsock.send("NICK " + self.nick + "\n")
			time.sleep(5)
			# Join the channel
			self.ircsock.send("JOIN "+ self.channel +"\r\n")
			self.sendmsg("Someone OP me plz!")
		except socket.gaierror:
			self.logger.warning("Connection error, trying again in 1 minute")
			time.sleep(60)
			self.connect()

	def activities(self, msg):
		# Check what activites should be done 
		if msg.find("PING :") != -1: 
			# Ping recieved from server	
			self.pong()
	  	if msg.find("JOIN :" + self.channel ) != -1:
	  		# Someone joined the channel
	  		n = self.get_nick(msg)
	  		for approved_nick in self.whitelist:
	  			if approved_nick.lower() in n.lower():
					self.op(n)
					break

	def pong(self):
		# Pong the server 
		self.ircsock.send("PONG :Pong\r\n") 

	def sendmsg(self, msg):
		# Send a message to the channel 
		self.ircsock.send("PRIVMSG "+ self.channel +" :"+ msg +"\r\n") 

	def op(self, to_op):
		# Op someone
		self.ircsock.send("MODE " + self.channel + " +o " + to_op + "\r\n")	

	def get_nick(self, data):
		# Retrieve the nick from a message							
		nick = data.split('!')[0]
		nick = nick.replace(':', ' ')
		nick = nick.replace(' ', '')
		nick = nick.strip(' \t\n\r')
		return nick


if __name__ == "__main__":
	bot = OpBot()
	bot.execute()