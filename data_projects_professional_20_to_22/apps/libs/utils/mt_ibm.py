import sys
from ibm_watson import LanguageTranslatorV3
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator


class MTIBM:
	def send(self, src_lang_code, dst_lang_code, text):
		translation = ''

		try:
			response = self.__language_translator.translate(
				text=text,
				model_id='{}-{}'.format(src_lang_code, dst_lang_code)).get_result()

			translation = response['translations'][0]['translation']
			if text == translation:
				translation = ''
		except:
			print('[MINOR][mt_ibm.send] %s' % str(sys.exc_info()).replace('"', ' '))

		return translation


	def __init__(self, name, config):
		self.name = name

		authenticator = IAMAuthenticator(config.mt_ibm_key)
		self.__language_translator = LanguageTranslatorV3(
			version=config.mt_ibm_version,
			authenticator=authenticator)
		self.__language_translator.set_service_url(config.mt_ibm_url)
