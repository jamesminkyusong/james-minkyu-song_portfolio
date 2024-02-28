import getopt
import os
import sys

from libs.utils.code_books import FileFormat
from libs.utils.code_books import LanguageFormat


class CMDOpts:
	'''
	option                  | required | variable                 | value_needed
	------------------------+----------+--------------------------+-------------
	-p                      |          | path                     | *
	-o                      |          | output_file              | *
	--add_count_in_filename |          | is_add_count_in_filename |
	-c                      |          | count                    | *
	-r                      |          | is_shuffle               |
	-m                      |          | max_rows_in_file         | *
	--not_add_sid           |          | is_add_sid               |
	-i                      |          | input_files              | * (comma-separated)
	--input_files_list      |          | input_files_list         | *
	--col_indices           |          | col_indices              | * (comma-separated)
	--col_names             |          | col_names                | * (comma-separated)
	--sheet_index           |          | sheet_index              | *
	--start_row             |          | start_row                | *
	--lang_format           |          | lang_format              | * (iso639 | bcp47)
	-s                      |          | is_noti_to_slack         |
	'''

	is_loaded = True

	short_opts = 'c:i:m:o:p:rs'
	long_opts = [
		'add_count_in_filename',
		'not_add_sid',
		'input_files_list=',
		'col_indices=',
		'col_names=',
		'sheet_index=',
		'start_row=',
		'lang_format='
	]

	path = None
	output_file = None
	output_file_format = FileFormat.XLSX
	is_add_count_in_filename = False
	count = sys.maxsize
	is_shuffle = False
	max_rows_in_file = 100000
	is_add_sid = True
	input_files = []
	input_files_list = None
	col_indices = []
	col_names = []
	sheet_index = 0
	start_row = 1
	lang_format = LanguageFormat.ISO639
	is_noti_to_slack = False


	def __parse(self, argv):
		opts, _ = getopt.getopt(argv, self.short_opts, self.long_opts)
		for opt, arg in opts:
			if opt == '-p':
				self.path = arg
			elif opt == '-o':
				self.output_file = arg
				file_ext = self.output_file.rsplit('.', 1)[1]
				self.output_file_format = next((item for item in FileFormat if item.value == file_ext), FileFormat.XLSX)
			elif opt == '--add_count_in_filename':
				self.is_add_count_in_filename = True
			elif opt == '-c':
				self.count = int(arg)
			elif opt == '-r':
				self.is_shuffle = True
			elif opt == '-m':
				self.max_rows_in_file = int(arg)
			elif opt == '--not_add_sid':
				self.is_add_sid = False
			elif opt == '-i':
				if not self.input_files:
					self.input_files = arg.split(',')
			elif opt == '--input_files_list':
				input_files_list_with_path = f'{self.path}/{arg}'
				if os.path.exists(input_files_list_with_path):
					with open(input_files_list_with_path) as f:
						self.input_files = [line.strip() for line in f.readlines()]
			elif opt == '--col_indices':
				self.col_indices = [int(x) for x in arg.split(',')]
			elif opt == '--col_names':
				self.col_names = arg.split(',')
			elif opt == '--sheet_index':
				self.sheet_index = int(arg)
			elif opt == '--start_row':
				self.start_row = int(arg)
			elif opt == '--lang_format':
				self.lang_format = next((item for item in LanguageFormat if item.value == arg), LanguageFormat.ISO639)
			elif opt == '-s':
				self.is_noti_to_slack = True


	def is_all_input_files_exist(self):
		return all([os.path.exists(f'{self.path}/{input_file}') for input_file in self.input_files])


	def __init__(self, name, argv):
		self.name = name
		self.__parse(argv)
