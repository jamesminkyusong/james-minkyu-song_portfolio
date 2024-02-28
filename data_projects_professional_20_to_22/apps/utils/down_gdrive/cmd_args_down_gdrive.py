from libs.utils.cmd_args import CMDArgs


class CMDArgsDownGdrive(CMDArgs):
	__child_args = [
		[['--drive_id'], {'type': str, 'help': 'gdrive id'}],
		[['--sub_dirs'], {'default': False, 'action': 'store_true', 'dest': 'is_fetch_sub_dirs', 'help': 'fetch sub dirs'}],
		[['--download'], {'default': False, 'action': 'store_true', 'dest': 'is_download', 'help': 'download'}],
		[['--extentions'], {'type': str, 'nargs': '*', 'help': 'extentions'}],
	]


	def __init__(self, name, required_args=None):
		self.name = name
		self.args += self.__child_args
		super().__init__(name, required_args)
