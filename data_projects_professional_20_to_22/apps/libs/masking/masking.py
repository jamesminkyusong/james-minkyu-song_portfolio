from datetime import datetime
import os
import re


class Masking:
	__pattern_email = '[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
	__pattern_url = re.compile('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\), ]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
	__re_credit_card_1 = re.compile('[0-9]{4}-[0-9]{4}-[0-9]{4}-[0-9]{4}')
	__re_credit_card_2 = re.compile('[0-9]{4}-[0-9]{6}-[0-9]{5}')
	__re_credit_card_3 = re.compile('[0-9]{16}')
	__re_tel = re.compile('[0-9]{2,3}-[0-9]{3,4}-[0-9]{4,4}')


	def execute(self, text):
		steps = [
			self.__filter_email,
			self.__filter_number_piis,
			self.__filter_url
		]

		for step in steps:
			before_text, text = text, step(text)
			if before_text != text:
				self.__show_before_and_after(before_text, text)

		return text


	def __filter_number_piis(self, text):
		for re_credit_card in [self.__re_credit_card_1, self.__re_credit_card_2, self.__re_credit_card_3, self.__re_tel]:
			piis = re_credit_card.findall(text)
			masked_piis = [''.join(['0' if c.isdigit() else c for c in p]) for p in piis]
			for before, after in zip(piis, masked_piis):
				text = text.replace(before, after)

		return text


	def __show_before_and_after(self, before, after):
		with open(self.__masking_log, 'a+') as f:
			message = (
				'===== =====\n'
				f'[<--] {before}\n'
				f'[-->] {after}\n'
			)
			f.write(message)
			f.close()


	def __init__(self, name):
		self.name = name
		self.__filter_email = lambda text: re.sub(self.__pattern_email, 'email@domain', text) if isinstance(text, str) else str(text)
		self.__filter_url = lambda text: re.sub(self.__pattern_url, 'url', text) if isinstance(text, str) else str(text)
		self.__masking_log = os.environ['PYTHONPATH'] + '/logs/masking_' + str(datetime.now()).split('.')[0].replace('-', '').replace(':', '').replace(' ', '_') + '.log'
