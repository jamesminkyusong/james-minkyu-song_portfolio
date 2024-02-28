from num2words import num2words
import inflect
import re
import regex
import unicodedata as ud


class TextUtils:
	__lang_codes = ['ar', 'de', 'en', 'es', 'fr', 'hi', 'id', 'ja', 'ko', 'ms', 'ne', 'pt', 'ru', 'th', 'tl', 'tr', 'vi', 'zh']
	__abbrs = {
		'ma\'am': 'madam', \
		'cannot': 'can not', \
		'can\'t': 'can not', \
		'n\'t': ' not', \
		'\'d': ' would', \
		'\'m': ' am', \
		'\'ll': ' will', \
		'\'re': ' are', \
		'\'s': ' is', \
		'\'ve': ' have', \
		'a.m': 'am',\
		'p.m': 'pm'}
	__ordinal_num2word_map = {}


	def is_supported(self, lang_code):
		return lang_code in self.__lang_codes


	def get_re_lang(self, lang_code):
		if lang_code == 'ar':
			return regex.compile(r'[\p{Arabic}]+')
		elif lang_code == 'ja':
			return regex.compile(r'([\p{Han}\p{Bopo}\p{Hira}\p{Katakana}]+)')
		elif lang_code == 'ko':
			return regex.compile(r'[\p{Hangul}]+')
		elif lang_code == 'th':
			return regex.compile(r'[\p{Thai}]+')
		# TO-DO: 베트남어 동작하지 않음. 확인 필요.
		# elif lang_code == 'vi':
		# return regex.compile(r'[\p{Tai_Viet}]+')
		elif lang_code == 'zh':
			return re.compile(r'[\u4e00-\u9fff]+')
		else:
			return regex.compile(r'([\p{Latin}\p{Latin_Extended_A}\p{Latin_Extended_Additional}\p{Latin_Extended_B}\p{Latin_Extended_C}\p{Latin_Extended_D}\p{Latin_Extended_E}\']+)')


	def get_lengths(self, lang_code, texts):
		if lang_code in ['ja', 'zh']:
			re_lang = self.get_re_lang(lang_code)
			return [len(''.join(re_lang.findall(text))) for text in texts]
		elif lang_code == 'th':
			re_th = self.get_re_lang(lang_code)
			return [sum(1 for cp in ''.join(re_th.findall(text)) if ud.category(cp)[0] != 'M') for text in texts]
		else:
			return [len(text.split(' ')) for text in texts]


	def normalize_en_text(self, text):
		text = text.lower()

		# i'm -> i am
		for k, v in self.__abbrs.items():
			text = text.replace(k, v)

		# my name is james(ジェームズ). -> my name is james
		re_en = re.compile('[a-z0-9]+')
		words = re_en.findall(text)

		# 1st -> first
		words = [self.__ordinal_num2word_map.get(word, word) for word in words]

		# 10 -> ten
		words = [(num2words(word).replace('-', ' ').replace(',', ' and') if word.isnumeric() else word) for word in words]

		return ' '.join(words)


	def __init__(self, name, lang_code='unknown'):
		self.name = name

		if lang_code == 'en':
			p = inflect.engine()
			for i in range(1, 100):
				word = p.number_to_words(i)		# 1 -> one
				ordinal_word = p.ordinal(word)	# one -> first
				ordinal_num = p.ordinal(i)		# 1 -> 1st
				self.__ordinal_num2word_map[ordinal_num] = ordinal_word	# 1st -> first
