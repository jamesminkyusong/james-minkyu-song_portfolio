from libs.utils.cmd_args import CMDArgs
from filters import Filters


class CMDArgsQuality(CMDArgs):
	__child_args = [
		[['--add_filter_result'], {'action': 'store_true', 'default': False, 'dest': 'is_add_filter_result', 'help': 'add filter result'}],
		[['--not_check_verb'], {'action': 'store_false', 'default': True, 'dest': 'is_check_verb', 'help': 'not check verb'}],
		[['--not_check_one_text'], {'action': 'store_false', 'default': True, 'dest': 'is_check_one_text', 'help': 'not check one text'}],
		[['--not_check_profanity'], {'action': 'store_false', 'default': True, 'dest': 'is_check_profanity', 'help': 'not check profanity'}],
		[['--not_check_similarity'], {'action': 'store_false', 'default': True, 'dest': 'is_check_similarity', 'help': 'not check similarity'}],
		[['--not_check_in_flitto'], {'action': 'store_false', 'default': True, 'dest': 'is_check_in_flitto', 'help': 'not check in flitto'}],
		[['--compare_en_words'], {'action': 'store_true', 'default': False, 'dest': 'is_compare_en_words', 'help': 'compare english words in two sentences'}],
		[['--drop_if_email'], {'action': 'store_true', 'default': False, 'dest': 'is_drop_if_email', 'help': 'drop if a text contains email'}],
		[['--drop_if_tel'], {'action': 'store_true', 'default': False, 'dest': 'is_drop_if_tel', 'help': 'drop if a text contains telephone number'}],
		[['--drop_if_url'], {'action': 'store_true', 'default': False, 'dest': 'is_drop_if_url', 'help': 'drop if a text contains url'}],
		[['--drop_if_alphabet'], {'action': 'store_true', 'default': False, 'dest': 'is_drop_if_alphabet', 'help': 'drop if a text contains alphabets'}],
		[['--drop_if_chinese'], {'action': 'store_true', 'default': False, 'dest': 'is_drop_if_chinese', 'help': 'drop if a text contains chinese'}],
		[['--drop_if_korean'], {'action': 'store_true', 'default': False, 'dest': 'is_drop_if_korean', 'help': 'drop if a text contains korean'}],
		[['--drop_if_no_korean'], {'action': 'store_true', 'default': False, 'dest': 'is_drop_if_no_korean', 'help': 'drop if a text contains no korean'}],
		[['--drop_if_number'], {'action': 'store_true', 'default': False, 'dest': 'is_drop_if_number', 'help': 'drop if a text contains numbers'}],
		[['--not_masking_piis'], {'action': 'store_false', 'default': True, 'dest': 'is_masking_piis', 'help': 'mask PIIs(Personal Identifiable Information)'}],
		[['--max_words_count'], {'type': int, 'help': 'max words count'}],
		[['--min_words_count'], {'type': int, 'default': 5, 'help': 'min words count'}],
		[['--max_chars_count'], {'type': int, 'help': 'max chars count'}],
		[['--min_chars_count'], {'type': int, 'default': 10, 'help': 'min chars count'}],
		[['--max_len_ratio'], {'type': int, 'default': 0, 'help': 'max ratio of long_text/short_text'}],
		[['--similarity_col_name'], {'help': 'similarity col name'}],
		[['--similarity_sid_col_name'], {'help': 'similarity col name for sid'}],
		[['--max_similarity'], {'type': float, 'default': 0.9, 'help': 'max similarity'}],
		[['--mt_sample_ratio'], {'type': int, 'default': 1, 'help': 'max similarity'}],
		[['--mt_lang_codes'], {'type': str, 'nargs': 2, 'help': 'src_lang_code and to_lang_code to translate'}]
	]


	def __validate(self):
		if self.values.mt_lang_codes is None:
			self.values.mt_lang_codes = []

		message = None

		if not self.is_all_input_files_exist():
			message = 'File(s) don\'t exist in -i/--input_files or --input_files_list'
		elif self.values.similarity_col_name and self.values.similarity_col_name not in self.values.col_names:
			message = '--similarity_col_name should be in --col_names!'

		if message:
			self.parser.error(message)


	def __set_filters(self):
		filters = Filters('filters')
		filters.is_add_filter_result = self.values.is_add_filter_result
		filters.is_check_verb = self.values.is_check_verb
		filters.is_check_one_text = self.values.is_check_one_text
		filters.is_check_profanity = self.values.is_check_profanity
		filters.is_check_similarity = self.values.is_check_similarity
		filters.is_check_in_flitto = self.values.is_check_in_flitto
		filters.is_drop_if_email = self.values.is_drop_if_email
		filters.is_drop_if_tel = self.values.is_drop_if_tel
		filters.is_drop_if_url = self.values.is_drop_if_url
		filters.is_drop_if_alphabet = self.values.is_drop_if_alphabet
		filters.is_drop_if_chinese = self.values.is_drop_if_chinese
		filters.is_drop_if_korean = self.values.is_drop_if_korean
		filters.is_drop_if_no_korean = self.values.is_drop_if_no_korean
		filters.is_drop_if_number = self.values.is_drop_if_number
		filters.is_compare_en_words = self.values.is_compare_en_words
		if self.values.max_words_count:
			filters.max_words_count = self.values.max_words_count
		filters.min_words_count = self.values.min_words_count
		if self.values.max_chars_count:
			filters.max_chars_count = self.values.max_chars_count
		filters.min_chars_count = self.values.min_chars_count
		filters.max_len_ratio = self.values.max_len_ratio
		filters.similarity_col_name = self.values.similarity_col_name
		filters.similarity_sid_col_name = self.values.similarity_sid_col_name
		filters.max_similarity = self.values.max_similarity
		filters.mt_sample_ratio = self.values.mt_sample_ratio
		filters.mt_lang_codes = self.values.mt_lang_codes
		self.values.filters = filters


	def __init__(self, name, required_args=None):
		self.name = name
		self.args += self.__child_args
		super().__init__(name, required_args)
		self.__validate()
		self.__set_filters()
