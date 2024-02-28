#!../../../bin/python3

import re

import pandas as pd

from libs.cleaning.cleaning_ja import CleaningJA
from libs.utils.cmd_args import CMDArgs
from libs.utils.df_utils import DFUtils


app_name = 'ja_refiner'
wrong_words = {
	'\'「': '「',
	'「\'': '「',
	'\'『': '『',
	'『\'': '『',
	'\'」': '」',
	'」\'': '」',
	'\'』': '』',
	'』\'': '』',
	'（': '(',
	'）': ')',
	'·': '・',
	'プラットホーム': 'プラットフォーム',
	'ブロックチェイン': 'ブロックチェーン',
	'新種コロナ': '新型コロナ',
	'新種のコロナ': '新型コロナ',
	'ピンテック': 'フィンテック',
	'三星電子': 'サムスン電子',
	'サムソン電子': 'サムスン電子',
	'小学校': '初等学校',
	'チェックカード': 'デビットカード',
	'都市銀行': '市中銀行',
	'微細ホコリ': '粒子状物質',
	'ウリ銀行': 'ウリィ銀行',
	'信用等級': '信用格付',
	'日本海': '東海',
	'文禄の役': '壬辰倭乱',
	'文禄・慶長の役': '壬辰倭乱',
	'華為技術': 'ファーウェイ',
	'銀行長': '頭取',
	'臺': '台',
	'國': '国',
	'靈': '霊',
	'眞': '真',
	'樂': '楽',
	'佛': '仏',
	'觀': '観',
	'禮': '礼',
	'彌': '弥',
	'藝': '芸',
	'經': '経',
	'敎': '教',
	'濟': '済',
	'縣': '県',
	'寶': '宝',
	'０': '0',
	'１': '1',
	'２': '2',
	'３': '3',
	'４': '4',
	'５': '5',
	'６': '6',
	'７': '7',
	'８': '8',
	'９': '9',
	'去る1': '1',
	'去る2': '2',
	'去る3': '3',
	'去る4': '4',
	'去る5': '5',
	'去る6': '6',
	'去る7': '7',
	'去る8': '8',
	'去る9': '9',
	'来る1': '1',
	'来る2': '2',
	'来る3': '3',
	'来る4': '4',
	'来る5': '5',
	'来る6': '6',
	'来る7': '7',
	'来る8': '8',
	'来る9': '9',
	'来たる1': '1',
	'来たる2': '2',
	'来たる3': '3',
	'来たる4': '4',
	'来たる5': '5',
	'来たる6': '6',
	'来たる7': '7',
	'来たる8': '8',
	'来たる9': '9',
	'コロナ禍': 'COVID-19',
	'コロナ19': 'COVID-19'}


def refine_line(line):
	is_refined = False
	is_manual_check_needed = False
	refined_line = line
	before_refined_line = line

	re_num = re.compile(r'[0-9],[0-9]')
	if refined_line.find(',') >= 0 and not re_num.search(refined_line):
		refined_line = refined_line.replace(',', '、')

	for wrong_word, right_word in wrong_words.items():
		refined_line = refined_line.replace(wrong_word, right_word)

	if refined_line.count('\'') % 2 == 0 and refined_line.count('"') == 0:
		quotation_is = [m.start() for m in re.finditer('\'', refined_line)]
		for i, quotation_i in enumerate(quotation_is):
			if i % 2 == 0:
				refined_line = refined_line[0:quotation_i] + '「' + refined_line[quotation_i+1:]
			else:
				refined_line = refined_line[0:quotation_i] + '」' + refined_line[quotation_i+1:]
	elif refined_line.count('"') % 2 == 0 and refined_line.count('\'') == 0:
		quotation_is = [m.start() for m in re.finditer('"', refined_line)]
		for i, quotation_i in enumerate(quotation_is):
			if i % 2 == 0:
				refined_line = refined_line[0:quotation_i] + '「' + refined_line[quotation_i+1:]
			else:
				refined_line = refined_line[0:quotation_i] + '」' + refined_line[quotation_i+1:]
	elif refined_line.count('\'') == 1 and refined_line.count('「') == 1:
		refined_line = refined_line.replace('\'', '」')
	elif refined_line.count('\'') == 1 and refined_line.count('」') == 1:
		refined_line = refined_line.replace('\'', '「')
	elif refined_line.count('\'') > 0 or refined_line.count('"') > 0:
		is_manual_check_needed = True

	if before_refined_line != refined_line:
		is_refined = True

	return is_refined, refined_line, is_manual_check_needed


def main():
	args_ja_refiner = CMDArgs('ja_refiner', ['path'])
	args = args_ja_refiner.values

	df = pd.read_excel(args.input_files_with_p[0])
	new_rows = []
	for row_i, row in df.iterrows():
		new_row = [row[0], row[1]]
		is_refined, refined_line, is_manual_check_needed = refine_line(row[2].strip())
		new_row += [refined_line, row[3], row[4]]
		if is_manual_check_needed:
			# new_row += [row[2].strip()]
			new_row += [refined_line]
		else:
			new_row += ['']

		new_rows += [new_row]

	output_file = '_refined.'.join(args.input_files_with_p[0].rsplit('/', 1)[1].rsplit('.', 1))
	new_df = pd.DataFrame(data=new_rows, columns=['sid', 'origin', 'translate', 'admin_qc_id', 'domain', 'manual'])
	df_utils = DFUtils('df_utils')
	df_utils.save(new_df, args.path, output_file)


if __name__ == '__main__':
	main()
