import sys
import requests

from libs.utils.code_books import TranslatorType


class MTDirect:
	__url = 'prod/mt'


	def send(self, src_lang, dst_lang, text):
		try:
			url = '%s/%s?mt=%s&src_lang_code=%s&dst_lang_code=%s&content=%s' \
				% (
					self.__host,
					self.__url,
					self.__mt_type,
					src_lang,
					dst_lang,
					text
				)
			response = requests.get(url)
			translation = response.json()['tr_content']
		except:
			print('[MINOR][mt.send] %s' % str(sys.exc_info()).replace('"', ' '))
			translation = ''

		return translation


	def __init__(self, name, config, translator_type=TranslatorType.GOOGLE):
		self.name = name
		self.__host = config.mt_direct_host
		self.__mt_type = translator_type.code()
