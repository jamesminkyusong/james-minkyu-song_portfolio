from libs.utils.code_books import FileFormat
from libs.utils.code_books import LanguageFormat


class RequestFormat:
	path = ''
	output_file = ''
	output_file_format = FileFormat.XLSX
	max_rows_in_file = 500_000
	lang_format = LanguageFormat.ISO639
	lang_ids = []
	lang_codes = []
	lang_names = []
	count = 1
	tag_id = 0
	tag_name = ''
	is_tagged_only = None
	is_not_tagged_only = None
	min_chars_count = 1
	min_words_count = 1
	include_company_id = 0
	exclude_company_ids = []


	def __init__(self, name):
		self.name = name
