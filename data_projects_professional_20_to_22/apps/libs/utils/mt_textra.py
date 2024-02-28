import json
import requests as req
import sys
from requests_oauthlib import OAuth1


class MTTextra:
	def send(self, src_lang_code, dst_lang_code, text):
		if src_lang_code == 'ja' and dst_lang_code == 'ko':
			url = self.__config.mt_textra_url_ja_ko
			# url = self.__config.mt_textra_url_ja_ko_colloquial
		elif src_lang_code == 'ko' and dst_lang_code == 'ja':
			url = self.__config.mt_textra_url_ko_ja
			# url = self.__config.mt_textra_url_ko_ja_colloquial
		else:
			return ''

		params = {
			'key': self.__config.mt_textra_key,
			'name': self.__config.mt_textra_name,
			'type': 'json',
			'text': text,
		}

		translation = ''
		try:
			res = req.post(url, data=params, auth=self.__consumer, timeout=60)
			res.encoding = 'utf-8'
			print('res.text: {}'.format(res.text))
			translation = json.loads(res.text)['resultset']['result']['text']
			if text == translation:
				translation = ''
		except:
			print('[MINOR][mt_textra.send] %s' % str(sys.exc_info()).replace('"', ' '))

		return translation


	def __init__(self, name, config):
		self.name = name
		self.__config = config
		self.__consumer = OAuth1(self.__config.mt_textra_key, self.__config.mt_textra_secret)


class MTTextra2:
	def send(self, src_lang_code, dst_lang_code, text):
		if src_lang_code == 'ja' and dst_lang_code == 'ko':
			url = self.__config.mt_textra_url_ja_ko
		elif src_lang_code == 'ko' and dst_lang_code == 'ja':
			url = self.__config.mt_textra_url_ko_ja
		else:
			return ''

		params = {
			'key': self.__config.mt_textra_keys[1],
			'name': self.__config.mt_textra_names[1],
			'type': 'json',
			'text': text,
		}

		translation = ''
		try:
			res = req.post(url, data=params, auth=self.__consumer)
			res.encoding = 'utf-8'
			print('res.text: {}'.format(res.text))
			translation = json.loads(res.text)['resultset']['result']['text']
			if text == translation:
				translation = ''
		except:
			print('[MINOR][mt_textra.send] %s' % str(sys.exc_info()).replace('"', ' '))

		return translation


	def __init__(self, name, config):
		self.name = name
		self.__config = config
		self.__consumer = OAuth1(self.__config.mt_textra_keys[1], self.__config.mt_textra_secrets[1])


class MTTextra3:
	def send(self, src_lang_code, dst_lang_code, text):
		if src_lang_code == 'ja' and dst_lang_code == 'ko':
			url = self.__config.mt_textra_url_ja_ko
		elif src_lang_code == 'ko' and dst_lang_code == 'ja':
			url = self.__config.mt_textra_url_ko_ja
		else:
			return ''

		params = {
			'key': self.__config.mt_textra_keys[2],
			'name': self.__config.mt_textra_names[2],
			'type': 'json',
			'text': text,
		}

		translation = ''
		try:
			res = req.post(url, data=params, auth=self.__consumer)
			res.encoding = 'utf-8'
			print('res.text: {}'.format(res.text))
			translation = json.loads(res.text)['resultset']['result']['text']
			if text == translation:
				translation = ''
		except:
			print('[MINOR][mt_textra.send] %s' % str(sys.exc_info()).replace('"', ' '))

		return translation


	def __init__(self, name, config):
		self.name = name
		self.__config = config
		self.__consumer = OAuth1(self.__config.mt_textra_keys[2], self.__config.mt_textra_secrets[2])
