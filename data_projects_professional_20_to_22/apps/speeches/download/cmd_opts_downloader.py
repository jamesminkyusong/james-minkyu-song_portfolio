from enum import Enum

from libs.utils.cmd_opts import CMDOpts


class ErrorCode(Enum):
	WRONG_COL_INDICES_NAMES_COUNT = ( \
		'[ERROR] Both COL_INDICES and COL_NAMES should have three values! (SID, USER_ID, URL)'
	)
	MISSING_REQUIRED_ARGUMENTS = ( \
		'Usage (required) :\n'
		'    ./2_donwloader.py -p PATH -i [INPUT_FILES] --col_indices SID_INDEX,USER_ID_INDEX,URL_INDEX --col_names SID,USER_ID_NAME,URL_NAME'
	)


class CMDOptsDownloader(CMDOpts):
	def __is_valid(self):
		error_code = None

		if not all([bool(x) for x in [self.path, self.input_files, self.col_indices, self.col_names]]):
			error_code = ErrorCode.MISSING_REQUIRED_ARGUMENTS
		elif not all([len(x) == 3 for x in [self.col_indices, self.col_names]]):
			error_code = ErrorCode.WRONG_COL_INDICES_NAMES_COUNT

		return error_code


	def __init__(self, name, argv):
		self.name = name
		super().__init__(name, argv)

		error_code = self.__is_valid()
		if error_code:
			self.is_loaded = False
			print(error_code.value)
