
import sys
import requests


class MT:
	def send(self, src_lang_code, dst_lang_code, text):
		new_lang_code = lambda lang_code: 'zh-CN' if lang_code == 'zh' else lang_code

		headers = {'Authorization': 'Bearer ' + self.__config.mt_token}
		data = {
			'src_lang_code': new_lang_code(src_lang_code),
			'dst_lang_code': new_lang_code(dst_lang_code),
			'contents': text
		}

		translation = ''
		try:
			response = requests.post(
				self.__config.mt_url,
				json=data,
				headers=headers
			)
			
			translation = response.json()['data']['translations'][0]['content']
			
		except:
			print(response.json())
			print('[MINOR][mt.send] %s' % str(sys.exc_info()).replace('"', ' '))

		return translation


	def __init__(self, config):
		self.__config = config