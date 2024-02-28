import pandas as pd

from libs.cleaning.cleaning_common import CleaningCommon
from libs.cleaning.cleaning_latin import CleaningLatin
from libs.cleaning.cleaning_ja import CleaningJA
from libs.cleaning.cleaning_ko import CleaningKO
from libs.cleaning.cleaning_zh import CleaningZH
from libs.masking.masking import Masking


class Reader:
	__cleanable_langs = ['de', 'en', 'es', 'fr', 'id', 'ja', 'ko', 'ms', 'pt', 'ru', 'tl', 'tr', 'vi', 'zh']
	__cleanable_non_latin_langs = ['ar', 'hi', 'ne', 'th']

	__cleaning_latin = CleaningLatin('cleaning_latin')
	__cleaning_non_latin = CleaningCommon('cleaning_non_latin')
	__cleaning_ja = CleaningJA('cleaning_ja')
	__cleaning_ko = CleaningKO('cleaning_ko')
	__cleaning_zh = CleaningZH('cleaning_zh')

	__masking = Masking('masking')


	def get_simple_df(self, input_file_p):
		ext_sep_map = {'bsv': '|', 'csv': ',', 'tsv': '\t'}
		ext = input_file_p.rsplit('.', 1)[-1]

		if ext in ext_sep_map.keys():
			df = pd.read_csv(input_file_p, sep=ext_sep_map[ext])
		elif ext == 'xlsx':
			df = pd.read_excel(input_file_p)
		else:
			with open(input_file_p) as f:
				lines = [line.strip() for line in f.readlines()]
			df = pd.DataFrame(data=lines[1:])
			df.columns = [lines[0]]

		return df


	def get_df(self, input_file_p, sheet_index, col_indices, col_names, start_row, nrows=None, is_add_cleaned_yn=False, is_masking_piis=True, is_remove_newline=False):
		file_ext = input_file_p[-3:].lower()
		is_text_file = file_ext in ['bsv', 'csv', 'tsv', 'txt']
		if is_text_file:
			sep = '\t' if file_ext in ['tsv', 'txt'] else '|' if file_ext == 'bsv' else ','

		if is_masking_piis:
			clean_f = lambda line, lang_code: self.__masking.execute(self.__clean(line, lang_code) if lang_code in self.__cleanable_langs else line)
		else:
			clean_f = lambda line, lang_code: self.__clean(line, lang_code) if lang_code in self.__cleanable_langs else line

		if len(col_indices) <= 0 and len(col_names) <= 0:
			if is_text_file:
				df = pd.read_csv(input_file_p, nrows=nrows+1, sep=sep)
			else:
				df = pd.read_excel(input_file_p, nrows=nrows+1, sheet_name=sheet_index)
		elif len(col_indices) <= 0:
			if is_text_file:
				df = pd.read_csv(input_file_p, usecols=col_names, nrows=nrows+1, sep=sep)
			else:
				df = pd.read_excel(input_file_p, usecols=col_names, nrows=nrows+1, sheet_name=sheet_index)
			if list(df.columns) != col_names:
				df = df[col_names]
		else:
			if is_text_file:
				df = pd.read_csv(input_file_p, usecols=col_indices, header=None, skiprows=start_row, nrows=nrows, sep=sep)[col_indices]
			else:
				df = pd.read_excel(input_file_p, usecols=col_indices, header=None, skiprows=start_row, nrows=nrows, sheet_name=sheet_index)[col_indices]
			df.columns = col_names

		if is_remove_newline:
			for col_name in df.columns:
				df[col_name] = df[col_name].apply(lambda row: row.replace('\n', ' ').strip() if isinstance(row, str) else row)

		lang_col_names = [col_name for col_name in col_names if col_name in self.__lang_codes]
		if is_add_cleaned_yn:
			for lang_col_name in lang_col_names:
				cleaned_text_df = df[lang_col_name].apply(lambda row: clean_f(row, lang_col_name))
				df[f'{lang_col_name}_cleaned'] = df[lang_col_name].combine(cleaned_text_df, lambda first, second: 'N' if first == second else 'Y')
				df[lang_col_name] = cleaned_text_df
		else:
			for lang_col_name in lang_col_names:
				df[lang_col_name] = df.apply(lambda row: clean_f(row[lang_col_name], lang_col_name), axis=1)

		return df


	def __clean(self, text, lang_code):
		if not isinstance(text, str):
			return text

		text = text.replace('\n', ' ').strip()
		if not text:
			return text

		if lang_code == 'ja':
			text, _ = self.__cleaning_ja.execute(text)
		elif lang_code == 'ko':
			text, _ = self.__cleaning_ko.execute(text)
		elif lang_code == 'zh':
			text, _ = self.__cleaning_zh.execute(text)
		elif lang_code in self.__cleanable_non_latin_langs:
			text, _ = self.__cleaning_non_latin.execute(text)
		elif lang_code in self.__cleanable_langs:
			text, _ = self.__cleaning_latin.execute(text)

		return text


	def __init__(self, name, lang_codes=[]):
		self.name = name
		self.__lang_codes = lang_codes
