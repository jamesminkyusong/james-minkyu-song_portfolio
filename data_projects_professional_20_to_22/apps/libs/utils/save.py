import csv
import math
from datetime import datetime

from libs.utils.code_books import FileFormat
from libs.utils.code_books import LanguageFormat
from libs.utils.tmx import TMX


class Save:
	def as_file(self, df, path, output_file):
		file_format = self.__parse_format(output_file)

		if file_format == FileFormat.BSV:
			save_func = self.__save_as_bsv
		elif file_format == FileFormat.CSV:
			save_func = self.__save_as_csv
		elif file_format == FileFormat.TMX:
			save_func = self.__save_as_tmx
		elif file_format == FileFormat.TSV:
			save_func = self.__save_as_tsv
		elif file_format == FileFormat.TXT:
			save_func = self.__save_as_txt
		else:
			save_func = self.__save_as_xlsx

		if self.__not_divide_output:
			sliced_dfs = [df]
		elif self.__rows_count_in_files:
			sliced_dfs = self.__slice_by_diff_rows_count(df, self.__max_rows_in_file, self.__rows_count_in_files)
		else:
			sliced_dfs = self.__slice(df, self.__max_rows_in_file)

		if len(sliced_dfs) > 1:
			print('{} [INFO][save.as_file] Slice {:,} rows to {} dfs'.format(self.__now_s(), len(df), len(sliced_dfs)))
			output_file_prefix, output_file_format = [x for x in output_file.split('.')]
			for index, sliced_df in enumerate(sliced_dfs):
				new_output_file = '%s_%d.%s' % (output_file_prefix, index + 1, output_file_format)
				save_func(sliced_df, path, new_output_file)
				print('{} [INFO][save.as_file] {:,} rows saved in {}'.format(self.__now_s(), len(sliced_df), new_output_file))
			print('{} [INFO][save.as_file] All saved to {} sliced files'.format(self.__now_s(), len(sliced_dfs)))
		else:
			save_func(df, path, output_file)
			print('{} [INFO][save.as_file] {:,} rows saved in {}'.format(self.__now_s(), len(df), output_file))


	def __save_as_bsv(self, df, path, output_file):
		df.to_csv(
			'%s/%s' % (path, output_file),
			index=False,
			header=self.__is_add_header,
			sep='|')


	def __save_as_csv(self, df, path, output_file):
		df.to_csv(
			'%s/%s' % (path, output_file),
			index=False,
			header=self.__is_add_header,
			sep=',')


	def __save_as_tmx(self, df, path, output_file):
		tmx = TMX('tmx', self.__lang_format)
		col_names = list(df.columns)[1:]
		for row in df.values:
			tmx.add_translation(row[0], col_names, row[1:])
		tmx.save(path, output_file)


	def __save_as_tsv(self, df, path, output_file):
		df.to_csv(
			'%s/%s' % (path, output_file),
			index=False,
			header=self.__is_add_header,
			sep='\t',
			quoting=csv.QUOTE_NONE)


	def __save_as_txt(self, df, path, output_file):
		with open('%s/%s' % (path, output_file), 'w') as f:
			if self.__is_add_header:
				f.write(df.columns[0] + '\n')
			for row in df[df.columns[0]]:
				f.write(row + '\n')
		f.close()


	def __save_as_xlsx(self, df, path, output_file):
		df.to_excel(
			'%s/%s' % (path, output_file),
			index=False,
			header=self.__is_add_header,
			engine='xlsxwriter')


	def __slice(self, df, max_rows):
		slices_count = math.ceil(len(df) / max_rows)
		return [df.iloc[(max_rows * index):min(len(df), max_rows * (index + 1)), :] for index in range(slices_count)]


	def __slice_by_diff_rows_count(self, df, max_rows, rows_count_in_files):
		dfs = []

		start_i, end_i = 0, 0
		for rows_count_in_file in rows_count_in_files:
			if (start_i + rows_count_in_file) >= len(df):
				break
			end_i = start_i + rows_count_in_file
			dfs += [df.iloc[start_i:end_i, :]]
			start_i = end_i

		if (len(df) - end_i) > max_rows:
			dfs += self.__slice(df.iloc[end_i:len(df), :], self.__max_rows_in_file)
		else:
			dfs += [df.iloc[end_i:len(df)]]

		return dfs


	def __init__(self, name, not_divide_output=False, max_rows_in_file=500_000, rows_count_in_files=[], lang_format=LanguageFormat.ISO639, is_add_header=True):
		self.name = name
		self.__not_divide_output = not_divide_output
		self.__max_rows_in_file = max_rows_in_file
		self.__rows_count_in_files = rows_count_in_files
		self.__lang_format = lang_format
		self.__parse_format = lambda x: FileFormat(next((item.value for item in FileFormat if item.value == x.split('.')[-1]), 'xlsx'))
		self.__is_add_header = is_add_header

		self.__now_s = lambda: str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
