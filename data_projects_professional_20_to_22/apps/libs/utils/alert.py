import http.client
import sys

from config import Config


class Alert:
	def __get_color(self, level):
		color = '#36A64F'	# Green

		if level in ['CRITICAL', 'MAJOR']:
			color = '#F08080'	# Red
		elif level == 'MINOR':
			color = '#FFE4B5'	# Yellow
		elif level == 'TEST':
			color = '#5DADE2'	# Blue

		return color


	def send(self, level, message):
		color = self.__get_color(level)

		try:
			body = '{ \
				\"channel\": \"' + self.__config.slack_channel + '\", \
				\"username\": \"' + self.__config.slack_username + '\", \
				\"icon_emoji\": \"' + self.__config.slack_iconemoji + '\", \
				\"attachments\": [ { \
					\"color\": \"' + color + '\", \
					\"text\": \"' + message + '\" \
				} ] \
			}'
			connection = http.client.HTTPSConnection(self.__config.slack_host)
			connection.request('POST', self.__config.slack_url, body.encode('utf8'))
			_ = connection.getresponse()
		except:
			print('[MINOR][alert.send] %s' % str(sys.exc_info()).replace('"', ' ')) 


	def __init__(self, name):
		self.name = name
		self.__config = Config('config')
