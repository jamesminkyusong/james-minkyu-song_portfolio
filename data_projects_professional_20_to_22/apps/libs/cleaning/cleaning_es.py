from libs.cleaning.cleaning_latin import CleaningLatin


class CleaningES(CleaningLatin):
	__es_question_mark = ("¿", "?")
	__es_exclamation_mark = ("¡", "!")


	def execute(self, text):
		before_text = text
		text, _ = super().execute(text)

		steps = [
			self.__es_uppercase_at_head
		]
		text = self.execute_step_by_step(steps, before_text, text)

		return text, before_text != text


	def __es_uppercase_at_head(self, text):
		text = self.uppercase_at_head(text)
		for mark in [self.__es_question_mark, self.__es_exclamation_mark]:
			if text[0] != mark[0] and text[-1] == mark[1]:
				text = mark[0] + text
			if text[0] == mark[0] and text[1].islower():
				text = text[0] + text[1].upper() + text[2:]

		return text


	def __init__(self, name):
		super().__init__(name)
		self.name = name
