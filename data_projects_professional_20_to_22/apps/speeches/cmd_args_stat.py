from libs.utils.cmd_args import CMDArgs


class CMDArgsStat(CMDArgs):
	__child_args = [
		[['--lang_code'], {'help': 'lang_code'}],
		[['--stat_type'], {'help': 'stat_type'}]
	]


	def __validate(self):
		message = None

		if self.values.lang_code not in self.__lang_codes:
			message = '--lang_code is not valid!'
		elif self.values.stat_type not in self.__stat_types:
			message = '--stat_type is not valid!'

		if message:
			self.parser.error(message)


	def __init__(self, name, lang_codes, stat_types, required_args=None):
		self.name = name
		self.__lang_codes = lang_codes
		self.__stat_types = stat_types
		self.args += self.__child_args
		super().__init__(name, required_args)
		self.__validate()
