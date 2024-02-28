import sys


class Filters:
	is_add_filter_result = False
	is_check_verb = True
	is_check_one_text = True
	is_check_profanity = True
	is_check_similarity = True
	is_check_in_flitto = True
	is_drop_if_email = False
	is_drop_if_tel = False
	is_drop_if_url = False
	is_drop_if_alphabet = False
	is_drop_if_chinese = False
	is_drop_if_korean = False
	is_drop_if_number = False
	is_compare_en_words = False
	max_words_count = sys.maxsize
	min_words_count = 5
	max_chars_count = sys.maxsize
	min_chars_count = 10
	similarity_col_name = None
	similarity_sid_col_name = None
	max_similarity = 0.9
	mt_sample_ratio = 1
	mt_lang_codes = None


	def __init__(self, name):
		self.name = name
