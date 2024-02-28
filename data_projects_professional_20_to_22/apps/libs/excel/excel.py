import csv
import sys
import xlrd
from datetime import datetime

from libs.cleaning.cleaning_latin import CleaningLatin
from libs.cleaning.cleaning_ja import CleaningJA
from libs.cleaning.cleaning_ko import CleaningKO
from libs.cleaning.cleaning_zh import CleaningZH
from libs.utils.alert import Alert


class Excel:
	__cleanable_langs = ['de', 'en', 'es', 'fr', 'id', 'ja', 'ko', 'ms', 'pt', 'ru', 'tl', 'tr', 'vi', 'zh']
	__cleaning_latin = CleaningLatin('cleaning_latin')
	__cleaning_ja = CleaningJA('cleaning_ja')
	__cleaning_ko = CleaningKO('cleaning_ko')
	__cleaning_zh = CleaningZH('cleaning_zh')


	def read(self, input_file_with_path, sheet_index, col_indices, col_names, start_row):
		file_ext = input_file_with_path.split('.')[-1]
		if file_ext == 'csv':
			read_func = self.__read_csv
		else:
			read_func = self.__read_xlsx

		rows = read_func(input_file_with_path, sheet_index, col_indices, col_names, start_row)
		lang_indices = [index for index, col_name in enumerate(col_names) if col_name in self.__lang_codes]
		if lang_indices:
			rows = [row for row in rows if all([bool(row[index]) for index in lang_indices])]

		return rows


	def __read_xlsx(self, input_file_with_path, sheet_index, col_indices, col_names, start_row):
		print('%s [INFO][excel.read_xlsx] Opening: %s' % (str(datetime.now()), input_file_with_path))

		try:
			with xlrd.open_workbook(input_file_with_path) as workbook:
				sheet = workbook.sheet_by_index(sheet_index)
				rows = [[self.__clean_func(sheet.cell_value(row_index, col_index), col_name) for col_index, col_name in zip(col_indices, col_names)] for row_index in range(start_row, sheet.nrows)]
		except:
			message = '[excel.read_xlsx] %s / %s' % (input_file_with_path, str(sys.exc_info()).replace('"', ' '))
			self.__assert(message)

		return rows


	def __read_csv(self, input_file_with_path, sheet_index, col_indices, col_names, start_row):
		print('%s [INFO][excel.read_csv] Opening: %s' % (str(datetime.now()), input_file_with_path))

		try:
			with open(input_file_with_path) as f:
				rows = [[self.__clean_func(row[col_index], col_name) for col_index, col_name in zip(col_indices, col_names)] for row in csv.reader(f, delimiter = '|')]
				if start_row > 0:
					rows = rows[start_row:]
		except:
			message = '[excel.read_csv] %s / %s' % (input_file_with_path, str(sys.exc_info()).replace('"', ' '))
			self.__assert(message)

		return rows


	def __clean(self, text, lang_code):
		if type(text) != str:
			return text

		text = text.replace('\n', ' ').strip()
		if not text:
			return text

		if lang_code == 'ja':
			text, is_cleaned = self.__cleaning_ja.execute(text)
		elif lang_code == 'ko':
			text, is_cleaned = self.__cleaning_ko.execute(text)
		elif lang_code == 'zh':
			text, is_cleaned = self.__cleaning_zh.execute(text)
		elif lang_code in self.__cleanable_langs:
			text, is_cleaned = self.__cleaning_latin.execute(text)

		return text


	def __assert(self, message):
		print(message)
		self.__alert.send('critical', message)
		sys.exit()


	def __init__(self, name, lang_codes = []):
		self.name = name
		self.__lang_codes = lang_codes
		self.__alert = Alert('alert')
		self.__clean_func = lambda line, lang_code: self.__clean(line, lang_code) if lang_code in self.__cleanable_langs else line
