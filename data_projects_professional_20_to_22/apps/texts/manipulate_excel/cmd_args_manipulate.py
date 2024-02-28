from libs.utils.cmd_args import CMDArgs


class CMDArgsManipulate(CMDArgs):
	__child_args = [
		[['--not_masking_piis'], {'action': 'store_false', 'default': True, 'dest': 'is_masking_piis', 'help': 'mask PIIs(Personal Identifiable Information)'}],
		[['--check_col_name'], {'type': str, 'help': 'column name to check something'}],
		[['--check_col_names'], {'nargs': '*', 'default': [], 'help': 'column names to check something'}],
		[['--check_each_col'], {'action': 'store_true', 'default': False, 'dest': 'is_check_each_col'}],
		[['--add_cleaned_yn'], {'action': 'store_true', 'default': False, 'dest': 'is_add_cleaned_yn', 'help': 'add cleaned yn'}],
		[['--keep_first'], {'action': 'store_true', 'default': True, 'dest': 'is_keep_first', 'help': 'keep first among duplicated rows'}],
		[['--keep_last'], {'action': 'store_false', 'dest': 'is_keep_first', 'help': 'keep last among duplicated rows'}],
		[['--drop_empty'], {'action': 'store_true', 'dest': 'is_drop_empty', 'help': 'drop rows which have an empty column'}],
		[['--drop_not_empty'], {'action': 'store_true', 'dest': 'is_drop_not_empty', 'help': 'drop rows which don\'t have an empty column'}],
		[['--drop_keywords'], {'action': 'store_true', 'dest': 'is_drop_keywords', 'help': 'drop rows which have one of keywords at least'}],
		[['--drop_except_keywords'], {'action': 'store_true', 'dest': 'is_drop_except_keywords', 'help': 'drop rows which have one of keywords at least'}],
		[['--keywords'], {'nargs': '*', 'help': 'keywords'}],
		[['--keywords_file'], {'help': 'keywords file'}],
		[['--exact_keyword_matching'], {'action': 'store_true', 'default': False, 'dest': 'is_exact_keyword_matching', 'help': 'exact keyword matching'}],
		[['--start_with_keyword'], {'action': 'store_true', 'default': False, 'dest': 'is_start_with_keyword', 'help': 'drop/leave rows which start with one of keywords'}],
		[['--add_keywords_freq'], {'action': 'store_true', 'dest': 'is_add_keywords_freq', 'help': 'add frequency of keywords in a text'}],
		[['--leave_ko'], {'action': 'store_true', 'help': 'leave texts which have Korean characters'}],
		[['--leave_wrong_encodings'], {'action': 'store_true', 'help': 'leave texts which have wrong encodings'}],
		[['--is_include_uppercase'], {'action': 'store_true', 'help': 'count of words which characters are all capitals'}],
		[['--hcat'], {'action': 'store_true', 'dest': 'is_hcat', 'help': 'merge vertically'}],
		[['--diff_and_intersect'], {'action': 'store_true', 'dest': 'is_diff_and_intersect', 'help': 'diff and intersect'}],
		[['--diff'], {'action': 'store_true', 'dest': 'is_diff', 'help': 'diff only'}],
		[['--intersect'], {'action': 'store_true', 'dest': 'is_intersect', 'help': 'intersect only'}],
		[['--drop_dup'], {'action': 'store_true', 'default': False, 'dest': 'is_drop_dup', 'help': 'drop all except one (check_col_names*)'}],
		[['--drop_almost_dup'], {'action': 'store_true', 'default': False, 'dest': 'is_drop_almost_dup', 'help': 'drop almost dup except one (check_col_names*)'}],
		[['--show_almost_dup_as_vertical'], {'action': 'store_true', 'default': False, 'dest': 'is_show_almost_dup_as_vertical'}],
		[['--drop_dup_all'], {'action': 'store_true', 'default': False, 'dest': 'is_drop_dup_all', 'help': 'drop all (check_col_names*)'}],
		[['--dup'], {'action': 'store_true', 'default': False, 'dest': 'is_dup', 'help': 'save duplicates by column (check_col_names*)'}],
		[['--lang_penalty'], {'action': 'store_true', 'default': False, 'dest': 'is_lang_penalty', 'help': 'compare only characters of a language (ignore numbers, punctuation marks and etc.)'}],
		[['--ignore_case'], {'action': 'store_true', 'default': False, 'dest': 'is_ignore_case', 'help': 'compare texts regardless of uppercase/lowercase'}],
		[['--full_scan'], {'action': 'store_true', 'default': False, 'dest': 'is_full_scan', 'help': 'scan texts fully during searching almost duplicated texts'}],
		[['--replace_from'], {'help': 'replace from'}],
		[['--replace_to'], {'default': "", 'help': 'replace to'}],
		[['--remove_newline'], {'action': 'store_true', 'default': False, 'dest': 'is_remove_newline', 'help': 'remove newline'}],
		[['--min_words_count'], {'type': int, 'default': 0, 'help': 'leave texts which has this count of words at least'}],
		[['--max_words_count'], {'type': int, 'default': 0, 'help': 'leave texts which has this count of words at most'}],
		[['--min_chars_count'], {'type': int, 'default': 0, 'help': 'leave texts which has this count of characters at least'}],
		[['--max_chars_count'], {'type': int, 'default': 0, 'help': 'leave texts which has this count of characters at most'}],
		[['--add_len'], {'action': 'store_true', 'dest': 'is_add_len', 'help': 'add words or chars count for language columns'}],
		[['--sort'], {'action': 'store_true', 'default': False, 'dest': 'is_sort', 'help': 'sort by column (check_col_name*)'}],
		[['--asc'], {'action': 'store_true', 'default': True, 'dest': 'is_asc', 'help': 'sort order by asc'}],
		[['--desc'], {'action': 'store_false', 'default': True, 'dest': 'is_asc', 'help': 'sort order by desc'}],
		[['--grammar_check'], {'action': 'store_true', 'dest': 'is_grammar_check', 'help': 'check grammar (only support Enlighs now)'}],
		[['--add_col_names'], {'nargs': '*', 'help': 'add column names'}],
		[['--add_col_values'], {'nargs': '*','default': '', 'help': 'add column values'}],
		[['--split'], {'action': 'store_true', 'default': False, 'dest': 'is_split', 'help': 'split by column (check_col_name*)'}],
		[['--sim_col_names'], {'type': str, 'nargs': 2, 'help': 'col_name1 and col_name2 to check similarity'}],
		[['--comp_len_col_names'], {'type': str, 'nargs': 2, 'help': 'col_name1 and col_name2 to check length'}],
		[['--max_len_ratio'], {'type': int, 'help': 'len(col_name1) / len(col_names2)'}]
	]


	def __validate(self):
		message = None

		if len(self.values.input_files_p) <= 0:
			message = 'No input files found'
		elif not self.values.is_ignore_not_found_files and not self.is_all_input_files_exist():
			message = 'File(s) don\'t exist in -i/--input_files or --input_files_list'
		elif not self.values.check_col_name and any([
				self.values.is_drop_empty,
				self.values.is_drop_not_empty,
				self.values.is_drop_keywords,
				self.values.is_drop_except_keywords,
				self.values.leave_ko,
				self.values.min_words_count > 0,
				self.values.max_words_count > 0,
				self.values.min_chars_count > 0,
				self.values.max_chars_count > 0
			]):
			message = '--check_col_name should be valid!'
		elif self.values.is_grammar_check and self.values.check_col_name != 'en':
			message = '--check_col_name should be en for checking grammar!'
		elif self.values.comp_len_col_names:
			if len(self.values.comp_len_col_names) != 2:
				message = '--comp_len_col_names should be two!'

		if message:
			self.parser.error(message)


	def __init__(self, name, required_args=None):
		self.name = name
		self.args += self.__child_args
		super().__init__(name, required_args)
		self.__validate()
