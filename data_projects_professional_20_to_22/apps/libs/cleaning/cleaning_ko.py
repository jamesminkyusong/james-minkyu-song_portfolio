from libs.cleaning.cleaning_common import CleaningCommon


class CleaningKO(CleaningCommon):
	def execute(self, text):
		before_text = text
		text, _ = super().execute(text)

		steps = [
			self.full_to_half_width_chars,
			self.full_to_half_width_fullstop,
			self.fullstop_mark_at_tail
		]
		text = self.execute_step_by_step(steps, before_text, text)

		return text, before_text != text


	def __init__(self, name):
		super().__init__(name)
		self.name = name
