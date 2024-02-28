from libs.utils.cmd_args import CMDArgs


class CMDArgsPreview(CMDArgs):
	__child_args = [
		[['--all'], {'action': 'store_true', 'default': False, 'dest': 'is_all', 'help': 'show all rows'}],
		[['--head'], {'type': int, 'default': 2, 'dest': 'head_count', 'help': 'show top HEAD rows'}],
		[['--tail'], {'type': int, 'default': 1, 'dest': 'tail_count', 'help': 'show bottom TAIL rows'}]
	]


	def __validate(self):
		message = None

		if not self.is_all_input_files_exist():
			message = 'File(s) don\'t exist in -i/--input_files or --input_files_list'

		if message:
			self.parser.error(message)


	def __init__(self, name, required_args=None):
		self.name = name
		self.args += self.__child_args
		super().__init__(name, required_args)
		self.__validate()
