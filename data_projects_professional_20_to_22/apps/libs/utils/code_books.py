from enum import Enum


class FileFormat(Enum):
	BSV = 'bsv'
	CSV = 'csv'
	TSV = 'tsv'
	TMX = 'tmx'
	TXT = 'txt'
	XLSX = 'xlsx'


class LanguageFormat(Enum):
	BCP47 = 'bcp47'
	ISO639 = 'iso639'


class TranslatorType(Enum):
	GOOGLE = 'google'
	YOUDAO = 'youdao'

	def code(self):
		if self == TranslatorType.YOUDAO:
			return 'y'

		return 'g'
