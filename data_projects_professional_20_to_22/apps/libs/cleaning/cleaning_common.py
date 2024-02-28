from datetime import datetime
import os
import string


class CleaningCommon:
	__end_marks = []
	__half_width_alphanum = ''
	__full_width_alphanum = ''
	__half_width_chars = ''
	__full_width_chars = ''


	def execute(self, text):
		before_text = text

		common_steps = [
			self.__spaces,
			self.__punctuation_marks,
			self.__newlines,
		]
		for common_step in common_steps:
			text = common_step(text)
		text = text.strip()

		return text, before_text != text


	def execute_step_by_step(self, steps, before_text, text):
		for step in steps:
			text = step(text)

		if before_text != text:
			self.__show_before_and_after(before_text, text)

		return text


	def __spaces(self, text):
		text = text.replace(u'\xa0', ' ')
		while '  ' in text:
			text = text.replace('  ', ' ')

		return text


	def __punctuation_marks(self, text):
		return text.replace('“', '"').replace('”', '"').replace('’', '\'').replace('‘', '\'')


	def __newlines(self, text):
		return text.replace('\n', ' ')


	def fullstop_mark_at_tail(self, text):
		if text[-1] in [',', ';', ':']:
			return text[:-1] + '.'
		elif text[-1] not in self.__end_marks:
			return text + '.'

		return text


	def full_to_half_width_chars(self, text):
		for src, dst in zip(self.__full_width_chars, self.__half_width_chars):
			text = text.replace(src, dst)

		return text


	def full_to_half_width_fullstop(self, text):
		return text.replace('。', '.')


	def full_to_half_width_alphanum(self, text):
		for src, dst in zip(self.__full_width_alphanum, self.__half_width_alphanum):
			text = text.replace(src, dst)

		return text


	def remove_space_between_CJ_words(self, text):
		index = -1
		while True:
			index = text.find(' ', index + 1)
			if index < 0:
				break
			if not (self.__is_alpha_num(text[index - 1]) \
				and self.__is_alpha_num(text[index + 1])):
				text = text[:index] + text[index + 1:]

		return text


	def uppercase_at_head(self, text):
		# capitalize()를 쓰면 첫번째 문자를 제외하고 모두 소문자로 변경하므로 쓰면 안됨
		# return text.capitalize()
		return text if text[0].isupper() else text[0].upper() + text[1:]


	def no_space_before_mark(self, text):
		text = text.replace(' ?', '?') \
			.replace(' !', '!') \
			.replace(' ,', ',') \
			.replace(' .', '.')

		return text


	def __is_alpha_num(self, char):
		if char in list(self.__half_width_alphanum) \
			or char in ['?', '!', '~']:
			return True

		return False


	def __show_before_and_after(self, before, after):
		with open(self.__cleaning_log, 'a+') as f:
			message = (
				'===== =====\n'
				f'[<--] {before}\n'
				f'[-->] {after}\n'
			)
			f.write(message)
			f.close()


	def __init__(self, name):
		self.name = name
		self.__end_marks = list('.?!~)…\'\"')
		self.__half_width_alphanum = string.digits + string.ascii_uppercase + string.ascii_lowercase
		self.__full_width_alphanum = '０１２３４５６７８９ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚ'
		self.__half_width_chars = '?!()~-.,' + self.__half_width_alphanum + ' '
		self.__full_width_chars = '？！（）～—．，' + self.__full_width_alphanum + '　'
		self.__cleaning_log = os.environ['PYTHONPATH'] + '/logs/cleaning_' + str(datetime.now()).split('.')[0].replace('-', '').replace(':', '').replace(' ', '_') + '.log'
