from libs.cleaning.cleaning_common import CleaningCommon


class CleaningJA(CleaningCommon):
	def execute(self, text):
		before_text = text
		text, _ = super().execute(text)

		steps = [
			self.full_to_half_width_chars,
			self.__ja_add_dot_at_tail,
			self.remove_space_between_CJ_words
		]
		text = self.execute_step_by_step(steps, before_text, text)

		return text, before_text != text


	def __ja_add_dot_at_tail(self, text):
		try:
			if text[-3:] == '...':
				return text
			elif text[-1] in ['"', '?', '!', '~', '・', '…']:
				return text
	
			if text[-1] in ['｡', '．', '、']:
				text = text[:-1] + '。'
			if text[-2:] in ['、。', '.。']:
				text = text[:-2] + '。'
			elif text[-2:] in ['"。', '?。', '!。', '~。', '・。', '…。']:
				text = text[:-1]
			elif text[-1] == '.' and text[-2] != '.':
				text = text[:-1] + '。'
			elif text[-1] != '。':
				text += '。'
		except:
			pass

		return text


	def __init__(self, name):
		super().__init__(name)
		self.name = name
