from libs.utils.cmd_args import CMDArgs


class CMDArgsBrokenIntegrities(CMDArgs):
	__child_args = [
		[['--dup_lang_in_group'], {'action': 'store_true', 'default': False, 'dest': 'is_dup_lang_in_group', 'help': 'extract corpora which are in same group though their languages are same'}]
	]


	def __init__(self, name, required_args=None):
		self.name = name
		self.args += self.__child_args
		super().__init__(name, required_args)
