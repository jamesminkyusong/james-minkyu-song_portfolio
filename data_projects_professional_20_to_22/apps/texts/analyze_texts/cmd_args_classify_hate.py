from libs.utils.cmd_args import CMDArgs


class CMDArgsClassifyHate(CMDArgs):
	__child_args = [
		[['--lang'], {'type': str, 'help': 'lang'}],
		[['--check_col_n'], {'type': str, 'help': 'check_col_n'}],
	]


	def __validate(self):
		message = None

		if not self.values.lang:
			message = 'No lang!'
		elif not self.values.check_col_n:
			message = 'No check_col_n!'

		if message:
			self.parser.error(message)


	def __init__(self, name, required_args=None):
		self.name = name
		self.args += self.__child_args
		super().__init__(name, required_args)
		self.__validate()
