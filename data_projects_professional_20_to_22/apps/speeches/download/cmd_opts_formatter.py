from enum import Enum

from libs.utils.cmd_opts import CMDOpts


class ErrorCode(Enum):
	MISSING_REQUIRED_ARGUMENTS = ( \
		'Usage (required) :\n'
		'    ./1_formatter.py -p PATH -o OUTPUT_FILE -i [INPUT_FILES] --col_indices [COL_INDICES] --col_names [COL_NAMES]\n'
		'Usage (optional) :\n'
		'    ./1_formatter.py -p PATH -o OUTPUT_FILE -i [INPUT_FILES] --col_indices [COL_INDICES] --col_names [COL_NAMES] -m 100000 -s'
	)


class CMDOptsFormatter(CMDOpts):
	def __is_valid(self):
		error_code = None

		if not all([bool(x) for x in [self.path, self.output_file, self.input_files, self.col_indices, self.col_names]]):
			error_code = ErrorCode.MISSING_REQUIRED_ARGUMENTS

		return error_code


	def __init__(self, name, argv):
		self.name = name
		super().__init__(name, argv)

		error_code = self.__is_valid()
		if error_code:
			self.is_loaded = False
			print(error_code.value)
