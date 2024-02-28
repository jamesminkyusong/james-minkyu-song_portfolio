from libs.utils.cmd_args import CMDArgs


class CMDArgsDB(CMDArgs):
	__child_args = [
		[['--lang_codes'], {'nargs': '*', 'help': 'language codes'}],
		[['--corpus_raw'], {'action': 'store_true', 'dest': 'is_from_corpus_raw', 'help': 'extract from corpus'}],
		[['--ignore_not_in_group'], {'action': 'store_true', 'dest': 'is_ignore_not_in_group', 'help': 'ignore corpora which are not in group'}],
		[['--no_cleaning'], {'action': 'store_false', 'default': True, 'dest': 'is_cleaning', 'help': 'no cleaning'}],
		[['--min_corpus_ids'], {'nargs': '*', 'help': 'corpus_id should be greater or equal than this'}],
		[['--exclude_lang_code'], {'help': 'exclude a row if this has a translation of this language'}],
		[['--include_company'], {'help': 'include a row if this has been delivered to this company'}],
		[['--exclude_companies'], {'type': str, 'nargs': '*', 'help': 'exclude a row if this has been delivered to this company'}],
		[['--add_ids'], {'action': 'store_true', 'dest': 'is_add_ids', 'help': 'add group_id and corpus_id'}],
		[['--add_delivery'], {'action': 'store_true', 'dest': 'is_add_delivery', 'help': 'add delivery'}],
		[['--add_tag'], {'action': 'store_true', 'dest': 'is_add_tag', 'help': 'add tag'}],
		[['--check_col_name'], {'help': 'check column name'}],
		[['--min_chars_count'], {'type': int, 'default': 1, 'help': 'the count of characters should be greater or equal than this'}],
		[['--min_words_count'], {'type': int, 'default': 1, 'help': 'the count of words should be greater or erqal than this'}],
		[['--tag'], {'help': 'tag'}],
		[['--tagged'], {'action': 'store_true', 'dest': 'is_tagged_only', 'help': 'only tagged-texts'}],
		[['--not_tagged'], {'action': 'store_true', 'dest': 'is_not_tagged_only', 'help': 'only not-tagged-texts'}],
		[['--newest'], {'action': 'store_true', 'default': True, 'dest': 'is_newest', 'help': 'sort by newest'}],
		[['--oldest'], {'action': 'store_false', 'dest': 'is_newest', 'help': 'sort by oldest'}]
	]


	def __init__(self, name, required_args=None):
		self.name = name
		self.args += self.__child_args
		super().__init__(name, required_args)
