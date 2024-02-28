import os

from libs.utils.cmd_args import CMDArgs


class CMDArgsMerge(CMDArgs):
	__child_args = [
		[['--lang_code'], {'help': 'lang code'}],
		[['--dup_file'], {'help': 'dup file'}],
		[['--update_db'], {'action': 'store_true', 'default': False, 'dest': 'is_update_db', 'help': 'update db'}]
	]


	def __init__(self, name, required_args=None):
		self.name = name
		self.args += self.__child_args
		super().__init__(name, required_args)
