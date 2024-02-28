import getopt
from enum import Enum

from libs.utils.cmd_opts import CMDOpts


class ErrorCode(Enum):
	LANG_CODES_SHOULD_BE_TWO = \
		'[ERROR] LANG_CODES should be LANG_CODE1,LANG_CODE2!'
	MISSING_REQUIRED_ARGUMENTS = ( \
		'Usage (required) :\n'
		'    ./db_to_excel.py -p PATH -o OUTPUT_FILE --lang_codes LANG_CODES\n'
		'Usage (optional) :\n'
		'    ./db_to_excel.py -p PATH -o OUTPUT_FILE -m MAX_ROWS_IN_FILE --lang_codes -c COUNT -s'
	)


class CMDOptsChild(CMDOpts):
	'''
	option       | required | variable   | value_needed
	-------------+----------+------------+-------------
	--lang_codes | *        | lang_codes | * (lang_code1,lang_code2)
	'''

	__child_long_opts = ['lang_codes=']

	lang_codes = []


	def __parse_more(self, argv):
		opts, _ = getopt.getopt(argv, self.short_opts, self.long_opts)
		for opt, arg in opts:
			if opt == '--lang_codes':
				self.lang_codes = arg.split(',')


	def __is_valid(self):
		error_code = None

		if len(self.lang_codes) != 2:
			error_code = ErrorCode.LANG_CODES_SHOULD_BE_TWO
		elif not all([self.path, self.output_file]):
			error_code = ErrorCode.MISSING_REQUIRED_ARGUMENTS

		return error_code


	def __init__(self, name, argv):
		self.name = name
		self.long_opts += self.__child_long_opts
		super().__init__(name, argv)
		self.__parse_more(argv)

		error_code = self.__is_valid()
		if error_code:
			self.is_loaded = False
			print(error_code.value)
