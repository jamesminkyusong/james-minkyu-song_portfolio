from libs.utils.cmd_args import CMDArgs


class CMDArgsCount(CMDArgs):
	__child_args = [
		[['--x_pairs'], {'type': int, 'help': 'x pairs'}],
		[['--lang_codes'], {'type': str, 'nargs': '*', 'help': 'lang codes'}],
		[['--exclude_company_ids'], {'type': int, 'nargs': '*', 'help': 'exclude a row if this has been delivered to this company'}],
		[['--update_db'], {'action': 'store_true', 'default': False, 'dest': 'is_update_db', 'help': 'update db'}],
		[['--save_excel'], {'action': 'store_true', 'default': False, 'dest': 'is_save_excel', 'help': 'save excel'}]
	]


	def __validate(self):
		message = None

		if isinstance(self.values.x_pairs, int) and not 1 <= self.values.x_pairs <= 4:
			message = '--x_pairs shoule be 1 ~ 4'
		elif self.values.is_save_excel and not all([self.values.path, self.values.output_file]):
			message = '-p/--path and -o/--output_file should be valid!'
		elif not self.values.x_pairs and not self.values.lang_codes:
			message = 'At least one of --x_pairs and --lang_codes should be valid!'

		if message:
			self.parser.error(message)


	def __init__(self, name, required_args=None):
		self.name = name
		self.args += self.__child_args
		super().__init__(name, required_args)
		self.__validate()
