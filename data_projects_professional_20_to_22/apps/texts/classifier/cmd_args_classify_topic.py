from libs.utils.cmd_args import CMDArgs


class CMDArgsClassifyTopic(CMDArgs):
	__child_args = [
		[['--method'], {'type': str, 'help': 'method'}],
		[['--rule_file'], {'type': str, 'default': '', 'help': 'rule_file'}],
		[['--lang'], {'type': str, 'help': 'lang'}],
		[['--text_col_n'], {'type': str, 'help': 'text_col_n'}],
		[['--step_interval'], {'type': int, 'default': 0, 'help': 'step_interval'}],
	]


	def __init__(self, name, required_args=None):
		self.name = name
		self.args += self.__child_args
		super().__init__(name, required_args)
