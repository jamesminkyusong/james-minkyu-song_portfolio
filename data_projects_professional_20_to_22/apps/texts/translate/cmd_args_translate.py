from libs.utils.cmd_args import CMDArgs


class CMDArgsTranslate(CMDArgs):
	__child_args = [
#		[['--mt_type'], {'choices': ['baidu', 'textra'], 'help': 'type of machine translate'}],
		[['--mt_type'], {'help': 'type of machine translate'}],
		[['--mt_lang_codes'], {'type': str, 'nargs': 2, 'help': 'src_lang_code and to_lang_code to translate'}],
		[['--threshold_count'], {'type': int, 'default': 5, 'help': 'threshold'}],
		[['--rows_count_per_iter'], {'type': int, 'default': 100, 'help': 'rows count per one iteration'}],
		[['--rows_count_per_call'], {'type': int, 'default': 1, 'help': 'rows count per one API call'}],
		[['--sleep_secs'], {'type': int, 'default': 0, 'help': 'sleep until next mt call'}],
		[['--verbose'], {'default': False, 'action': 'store_true', 'dest': 'is_verbose', 'help': 'show log'}]
	]


	def __init__(self, name, required_args=None):
		self.name = name
		self.args += self.__child_args
		super().__init__(name, required_args)
