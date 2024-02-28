from libs.utils.cmd_args import CMDArgs


class CMDArgsFind(CMDArgs):
	__child_args = [
		[['--corpus_col_i'], {'type': int, 'default': -1, 'help': 'corpus col i'}]
	]


	def __init__(self, name, required_args=None):
		self.name = name
		self.args += self.__child_args
		super().__init__(name, required_args)
