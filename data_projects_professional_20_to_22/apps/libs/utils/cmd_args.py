from datetime import datetime
import argparse
import os
import sys

from libs.utils.code_books import FileFormat, LanguageFormat


class CMDArgs:
	args = [
		[['--prod'], {'default': False, 'action': 'store_true', 'dest': 'is_production', 'help': 'production'}],
		[['-p', '--path'], {'help': 'path'}],
		[['-o', '--output_file'], {'help': 'output file'}],
		[['-c', '--count'], {'type': int, 'default': sys.maxsize, 'help': 'count'}],
		[['-r', '--shuffle'], {'default': False, 'action': 'store_true', 'dest': 'is_shuffle', 'help': 'shuffle'}],
		[['-m', '--max_rows_in_file'], {'type': int, 'default': 500_000, 'help': 'max rows in a file'}],
		[['--not_divide_output'], {'default': False, 'action': 'store_true', 'help': 'not divide output'}],
		[['--rows_count_in_files'], {'type': int, 'nargs': '*', 'help': 'rows count in files'}],
		[['--add_sid'], {'default': False, 'action': 'store_true', 'dest': 'is_add_sid', 'help': 'add sid at first'}],
		[['--not_add_header'], {'default': True, 'action': 'store_false', 'dest': 'is_add_header', 'help': 'not add header'}],
		[['--start_sid'], {'default': 1, 'type': int, 'help': 'start sid'}],
		[['-i', '--input_files'], {'nargs': '*', 'help': 'input files'}],
		[['--input_files_list'], {'help': 'input files list'}],
		[['--ignore_not_found_files'], {'action': 'store_true', 'dest': 'is_ignore_not_found_files', 'help': 'input files list'}],
		[['--col_indices'], {'type': int, 'nargs': '*', 'help': 'col indices'}],
		[['--col_names'], {'nargs': '*', 'help': 'col names'}],
		[['--sheet_index'], {'type': int, 'default': 0, 'help': 'sheet index'}],
		[['--start_row'], {'type': int, 'default': 1, 'help': 'start row'}],
		[['--lang_format'], {'choices': ['iso639', 'bcp47'], 'default': 'iso639', 'help': 'lang format'}],
		[['-s', '--noti_to_slack'], {'default': False, 'action': 'store_true', 'dest': 'is_noti_to_slack', 'help': 'send a message to slack'}]
	]


	def __set_required_args(self, required_args):
		required_args_set = set(required_args)

		for index, arg in enumerate(self.args):
			if set([option.replace('-', '') for option in arg[0]]) & required_args_set:
				self.args[index][1]['required'] = True


	def __parse(self):
		parser = argparse.ArgumentParser(description=self.name)
		for arg in self.args:
			parser.add_argument(*arg[0], **arg[1])
		args = parser.parse_args()

		if args.col_indices is None:
			args.col_indices = []
		if args.col_names is None:
			args.col_names = []

		args.input_files_p = []

		if args.input_files_list:
			input_files_list_p = args.input_files_list if args.input_files_list.count('/') > 0 else f'{args.path}/{args.input_files_list}'
			if os.path.exists(input_files_list_p):
				with open(input_files_list_p) as f:
					args.input_files = [line.strip() for line in f.readlines()]

		if args.input_files:
			args.input_files_p = [input_file if input_file.count('/') > 0 else f'{args.path}/{input_file}' for input_file in args.input_files]

		if args.is_ignore_not_found_files:
			args.input_files_p = list(filter(lambda x: os.path.exists(x), args.input_files_p))
	
		if args.output_file:
			file_ext = args.output_file.rsplit('.', 1)[-1]
			args.output_file_format = next((item for item in FileFormat if item.value == file_ext), FileFormat.XLSX)
		elif len(args.input_files_p) > 0:
			args.output_file = '_result.'.join(args.input_files_p[0].rsplit('/', 1)[-1].rsplit('.', 1))
	
		args.lang_format = next((item for item in LanguageFormat if item.value == args.lang_format), LanguageFormat.ISO639)

		return parser, args


	def is_all_input_files_exist(self):
		# return all([os.path.exists(input_file_with_p) for input_file_with_p in self.values.input_files_p])

		not_found_files = list(filter(lambda x: not os.path.exists(x), self.values.input_files_p))
		if len(not_found_files) == 0:
			return True
		else:
			for not_found_file in not_found_files:
				print('{} [CRITICAL][cmd_args.is_all_files_exist] Files not found: {}'.format(str(datetime.now()), not_found_file))
			return False


	def __init__(self, name, required_args=None):
		self.name = name
		if required_args:
			self.__set_required_args(required_args)
		self.parser, self.values = self.__parse()
