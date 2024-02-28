from libs.utils.cmd_args import CMDArgs


class CMDArgsSimilarity(CMDArgs):
	__child_args = [
		[['--id_col_name'], {'type': str, 'help': 'id col name'}],
		[['--lang_col_name'], {'type': str, 'help': 'lang col name'}],
		[['--min_similarity'], {'type': float, 'default': 0.9, 'help': 'min_similarity'}]
	]


	def __init__(self, name, required_args=None):
		self.name = name
		self.args += self.__child_args
		super().__init__(name, required_args)
