from urllib.parse import quote
import sys
import hashlib
import random
import requests


class MTBaidu:
	def send(self, src_lang_code, dst_lang_code, text):
		url = self.get_url(src_lang_code, dst_lang_code, text)

		translation = ''
		try:
			response = requests.get(
				url
			)
			translation = response.json()['trans_result'][0]['dst']
		except:
			print('[MINOR][mt_baidu.send] %s' % str(sys.exc_info()).replace('"', ' '))

		return translation


	def get_url(self, src_lang_code, dst_lang_code, text):
		salt = random.randint(32768, 65536)
		sign = self.__APP_ID + text + str(salt) + self.__SECRET_KEY
		sign = hashlib.md5(sign.encode()).hexdigest()
		url = self.__BASE_URL + self.__API_URL +'?appid=' + self.__APP_ID + '&q=' + quote(text) + '&from=' + src_lang_code + '&to=' + dst_lang_code + '&salt=' + str(salt) + '&sign=' + sign

		return url


	def __init__(self, name, config):
		self.name = name
		self.__config = config
		self.__APP_ID = '20190619000308802'
		self.__SECRET_KEY = 'gAuBfGBhy7uCY37JtlYk'
		self.__BASE_URL = 'http://api.fanyi.baidu.com'
		self.__API_URL = '/api/trans/vip/translate'
