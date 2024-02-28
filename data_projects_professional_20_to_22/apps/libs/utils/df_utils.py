from datetime import datetime
import math

import pandas as pd

from libs.utils.code_books import LanguageFormat
from libs.utils.save import Save
from libs.utils.similarity_calculator import SimilarityCalculator
from libs.utils.text_utils import TextUtils


app_name = 'df_utils'


class DFUtils:
	def __add_penalty_cols(self, df, col_names, is_lang_penalty=False, is_ignore_case=False):
		penalty_col_name_f = lambda lang_code: f'{lang_code}_penalty'
		compare_col_names = col_names[:]

		text_utils = TextUtils('text_utils')
		for col_name in col_names:
			if text_utils.is_supported(col_name):
				if is_lang_penalty and is_ignore_case:
					re_lang = text_utils.get_re_lang(col_name)
					penalty_f = lambda text: ''.join(re_lang.findall(text.lower()))
				elif is_lang_penalty:
					re_lang = text_utils.get_re_lang(col_name)
					penalty_f = lambda text: ''.join(re_lang.findall(text))
				else:
					penalty_f = lambda text: text.lower()
#				penalty_f = lambda text: text.strip().lower()

				penalty_col_name = penalty_col_name_f(col_name)
				df[penalty_col_name] = df[col_name].apply(penalty_f)
				compare_col_names[compare_col_names.index(col_name)] = penalty_col_name

		return compare_col_names


	def __drop_penalty_cols(self, df, col_names):
		penalty_col_names = [col_name for col_name in col_names if '_penalty' in col_name and col_name in list(df.columns)]
		if penalty_col_names:
			df.drop(columns=penalty_col_names, inplace=True)


	def add_sid(self, df, start=1):
		col_name = 'sid'
		if col_name in df.columns:
			df.drop(columns=col_name, inplace=True)

		df.insert(0, col_name, list(range(start, start + len(df))))


	def concat_h(self, dfs):
		df = pd.concat(dfs, axis=1)
		print('{} [INFO][{}.concat_h] {:,} rows merged'.format(str(datetime.now()), app_name, len(df)))
		return df


	def concat_v(self, dfs):
		df = pd.concat(dfs)
		df.reset_index(drop=True, inplace=True)
		print('{} [INFO][{}.concat_v] {:,} rows merged'.format(str(datetime.now()), app_name, len(df)))
		return df


	def diff_and_intersect(self, df1, df2, col_names, is_lang_penalty=False, is_ignore_case=False):
		compact_df1 = df1[col_names]
		compact_df2 = df2[col_names]

		if is_lang_penalty or is_ignore_case:
			compare_col_names = self.__add_penalty_cols(
				compact_df1,
				col_names,
				is_lang_penalty=is_lang_penalty,
				is_ignore_case=is_ignore_case)
			_ = self.__add_penalty_cols(
				compact_df2,
				col_names,
				is_lang_penalty=is_lang_penalty,
				is_ignore_case=is_ignore_case)
		else:
			compare_col_names = col_names[:]

		concat_df = pd.concat([compact_df1, compact_df2])
		diff_df = df1[~(concat_df.duplicated(subset=compare_col_names, keep=False).head(len(df1)))]
		intersect_df = df1[concat_df.duplicated(subset=compare_col_names, keep=False).head(len(df1))]

		if is_lang_penalty:
			self.__drop_penalty_cols(diff_df, compare_col_names)
			self.__drop_penalty_cols(intersect_df, compare_col_names)

		print('{} [INFO][{}.diff_and_intersect] diff {:,} rows and intersect {:,} rows in {:,} rows for {}'.format(str(datetime.now()), app_name, len(diff_df), len(intersect_df), len(df1), col_names))
		return diff_df, intersect_df


	def drop_column(self, df, col_name):
		df.drop(columns=col_name, inplace=True)


	def drop_duplicates(self, df, col_names, is_keep_first=True, is_lang_penalty=False, is_ignore_case=False, is_check_each_col=False):
		keep = 'first' if is_keep_first else 'last'
		len_df = len(df)
		if is_lang_penalty or is_ignore_case:
			compare_col_names = self.__add_penalty_cols(
				df,
				col_names,
				is_lang_penalty,
				is_ignore_case)
		else:
			compare_col_names = col_names[:]

		if is_check_each_col:
			i_col_name = 'result'
			all_dup_index = pd.DataFrame(data={i_col_name: [False] * len(df)})
			all_dropped_index = pd.DataFrame(data={i_col_name: [False] * len(df)})
			for col_name in compare_col_names:
				all_dup_index[i_col_name] |= df.duplicated(subset=col_name, keep=False)
				all_dropped_index[i_col_name] |= df.duplicated(subset=col_name, keep=keep)
			dup_df = df[all_dup_index[i_col_name]]
			dropped_df = df[all_dropped_index[i_col_name]]
			df = df[all_dropped_index[i_col_name] == False]
		else:
			dup_df = df[df.duplicated(subset=compare_col_names, keep=False)]
			dropped_df = df[df.duplicated(subset=compare_col_names, keep=keep)]
			df.drop_duplicates(subset=compare_col_names, keep=keep, inplace=True)

		if is_lang_penalty:
			for a_df in [df, dup_df, dropped_df]:
				self.__drop_penalty_cols(a_df, compare_col_names)

		message = '{} [INFO][{}.drop_duplicates]'.format(str(datetime.now()), app_name)
		if len(df) == len_df:
			message += ' Nothing dropped'
		else:
			message += ' {:,} rows dropped and {:,} rows alived in {:,} rows'.format(len(dropped_df), len(df), len_df)
		message += f' for {col_names}'
		print(message)
		return df, dup_df, dropped_df


	def drop_duplicates_all(self, df, col_names, is_lang_penalty=False, is_ignore_case=False):
		len_df = len(df)
		if is_lang_penalty or is_ignore_case:
			compare_col_names = self.__add_penalty_cols(
				df,
				col_names,
				is_lang_penalty=is_lang_penalty,
				is_ignore_case=is_ignore_case)
		else:
			compare_col_names = col_names[:]

		dropped_df = df[df.duplicated(subset=compare_col_names, keep=False)]
		df.drop_duplicates(subset=compare_col_names, keep=False, inplace=True)

		if is_lang_penalty:
			for a_df in [df, dropped_df]:
				self.__drop_lang_penalty_cols(a_df, compare_col_names)

		message = '{} [INFO][{}.drop_duplicates_all]'.format(str(datetime.now()), app_name)
		if len(df) == len_df:
			message += ' Nothing dropped'
		else:
			message += ' {:,} rows dropped and {:,} rows alived in {:,} rows'.format(len(dropped_df), len(df), len_df)
		message += f' for {col_names}'
		print(message)
		return df, dropped_df


	def drop_almost_duplicates(self, df, col_names, is_lang_penalty=False, sid_col_name='sid', is_full_scan=False, min_similarity=0.9, is_show_almost_dup_as_vertical=False):
		similarity_calculator = SimilarityCalculator('similarity_calculator', df)
		similar_df = similarity_calculator.get_similar_df(
			col_names[0],
			sid_col_name,
			is_full_scan,
			min_similarity,
			is_show_almost_dup_as_vertical)
		diff_df, _ = self.diff_and_intersect(df, similar_df, [sid_col_name])

		return diff_df, similar_df


	def get_duplicates(self, df, col_names, is_lang_penalty=False, is_ignore_case=False):
		if is_lang_penalty or is_ignore_case:
			compare_col_names = self.__add_penalty_cols(
				df,
				col_names,
				is_lang_penalty=is_lang_penalty,
				is_ignore_case=is_ignore_case)
		else:
			compare_col_names = col_names[:]

		dup_df = df[df.duplicated(subset=compare_col_names, keep=False)]
		dup_df.sort_values(by=compare_col_names, inplace=True)

		if is_lang_penalty:
			self.__drop_lang_penalty_cols(dup_df, compare_col_names)

		print('{} [INFO][{}.get_duplicates] {:,} rows duplicated in {:,} rows'.format(str(datetime.now()), app_name, len(dup_df), len(df)))
		return dup_df


	def ignore_wrong_encodings(self, df, col_names=None):
		if not col_names:
			return df

		encoding_filter = lambda text: text.encode('utf-8', 'surrogatepass').decode('utf-8', 'ignore') if isinstance(text, str) and any(0xD800 <= ord(c) <= 0xDFFF for c in text) else text
		for col_name in col_names:
			df[col_name] = df[col_name].apply(encoding_filter)

		return df


	def leave_wrong_encodings(self, df, col_names=None):
		if not col_names:
			return df

		leave_filter = lambda text: any(0xD800 <= ord(c) <= 0xDFFF for c in text) if isinstance(text, str) else False
		first_index = df[col_names[0]].apply(leave_filter)
		for col_name in col_names[1:]:
			second_index = df[col_name].apply(leave_filter)
			first_index = first_index.combine(second_index, lambda first, second: first or second)
		df = df[first_index]

		encoding_filter = lambda text: text.encode('utf-8', 'surrogatepass').decode('utf-8', 'replace')
		for col_name in col_names:
			df[col_name] = df[col_name].apply(encoding_filter)

		print('{} [INFO][{}.leave_wrong_encodings] {} wrong encodings found'.format(str(datetime.now()), app_name, len(df)))
		return df


	def save(self, df, path, output_file, not_divide_output=False, max_rows_in_file=500_000, rows_count_in_files=[], lang_format=LanguageFormat.ISO639, is_add_header=True, is_save_empty_df=True):
		if len(df) > 0 or is_save_empty_df:
			save = Save('save', not_divide_output, max_rows_in_file, rows_count_in_files, lang_format, is_add_header)
			save.as_file(df, path, output_file)
		else:
			print('{} [INFO][{}.save] Not save an empty df in {}'.format(str(datetime.now()), app_name, output_file))


	def save_multiple_sheets(self, dfs, path, output_file, sheet_names=[]):
		if len(sheet_names) <= 0:
			sheet_names = [f'Sheet{sheet_i}' for sheet_i in range(1, 1+len(dfs))]

		writer = pd.ExcelWriter(f'{path}/{output_file}', engine='xlsxwriter')
		for sheet_name, df in zip(sheet_names, dfs):
			df.to_excel(writer, sheet_name=sheet_name)
		writer.save()


	def shuffle(self, df):
		return df.sample(frac=1)


	def slice(self, df, max_rows):
		slices_count = math.ceil(len(df) / max_rows)
		return [df.iloc[(max_rows*i):min(len(df), max_rows*(i+1)), :] for i in range(slices_count)]


	def sort(self, df, col_names):
		df.sort_values(by=col_names, inplace=True)


	def __init__(self, name):
		self.name = name
