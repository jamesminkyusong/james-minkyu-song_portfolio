from enum import Enum

from libs.utils.cmd_opts import CMDOpts


class ErrorCode(Enum):
	NOT_EXIST_INPUT_FILES = (
		'[ERROR] INPUT_FILES don\'t exist!'
	)
	MISSING_REQUIRED_ARGUMENTS = (
		'Usage (required) :\n'
		'    ./annotator.py -p PATH -o OUTPUT_FILE -i [INPUT_FILES]'
	)


class CMDOptsChild(CMDOpts):
	def __is_valid(self):
		error_code = None

		if not all([self.path, self.output_file, self.input_files]):
			error_code = ErrorCode.MISSING_REQUIRED_ARGUMENTS
		elif not self.is_all_input_files_exist():
			error_code = ErrorCode.NOT_EXIST_INPUT_FILES

		return error_code


	def __init__(self, name, argv):
		self.name = name
		super().__init__(name, argv)

		error_code = self.__is_valid()
		if error_code:
			self.is_loaded = False
			print(error_code.value)
