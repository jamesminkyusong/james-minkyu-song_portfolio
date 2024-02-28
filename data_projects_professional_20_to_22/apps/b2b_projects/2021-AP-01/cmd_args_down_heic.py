from libs.utils.cmd_args import CMDArgs


class CMDArgsDownHeic(CMDArgs):
	__child_args = [
		[['--drive_id'], {'type': str, 'help': 'google drive id'}]
	]


	def __init__(self, name, required_args=None):
		self.name = name
		self.args += self.__child_args
		super().__init__(name, required_args)
