#!../../../bin/python3

from datetime import datetime

import pandas as pd

from cmd_args_refine import CMDArgsRefine
from libs.utils.alert import Alert
from libs.utils.df_utils import DFUtils
from libs.cleaning.cleaning_common import CleaningCommon
from libs.cleaning.cleaning_latin import CleaningLatin
from libs.cleaning.cleaning_ja import CleaningJA
from libs.cleaning.cleaning_ko import CleaningKO
from libs.cleaning.cleaning_zh import CleaningZH


app_name = 'refine'


def refine_df(input_file_p, is_append_refined_text):
	print('{} [INFO][{}.get_df] Reading from {} ...'.format(str(datetime.now()), app_name, input_file_p))

	lang_codes = ['ar', 'de', 'en', 'es', 'fr', 'hi', 'id', 'ja', 'ko', 'ms', 'ne', 'pt', 'ru', 'th', 'tl', 'tr', 'vi', 'zh']

	refine_latin = CleaningLatin('refine_latin')
	refine_non_latin = CleaningCommon('refine_common')
	refine_ja = CleaningJA('refine_ja')
	refine_ko = CleaningKO('refine_ko')
	refine_zh = CleaningZH('refine_zh')
	refine_map = {
		'ja': refine_ja,
		'ko': refine_ko,
		'zh': refine_zh,
		'ar': refine_non_latin,
		'hi': refine_non_latin,
		'ne': refine_non_latin,
		'th': refine_non_latin}

	df = pd.read_excel(input_file_p)
	for lang_col_name in [lang_col_name for lang_col_name in df.columns if lang_col_name in lang_codes]:
		refine_f = refine_map.get(lang_col_name, refine_latin)
		if is_append_refined_text:
			refined_texts = df[lang_col_name].apply(lambda text: '' if (refined_text := refine_f.execute(text)[0]) == text else refined_text, lang_col_name)
			df.insert(len(df.columns), f'refined_{lang_col_name}', refined_texts)
		else:
			refined_texts = df[lang_col_name].apply(lambda text: refine_f.execute(text))
			df[lang_col_name] = refined_texts

	print('{} [INFO][{}.get_df] {:,} rows fetched'.format(str(datetime.now()), app_name, len(df)))
	return df


def save_df(df, path, output_file, is_leave_refined_texts_only):
	if is_leave_refined_texts_only:
		for refined_col_name in [col_name for col_name in df.columns if 'refined_' in col_name]:
			df = df[df[refined_col_name] != '']

	df_utils = DFUtils('df_utils')
	df_utils.save(
		df,
		path,
		output_file,
		is_save_empty_df=False)


def main():
	args_refine = CMDArgsRefine('cmd_args_refine')
	args = args_refine.values

	output_file_f = lambda output_file: '_refined.'.join(output_file.rsplit('.', 1)).rsplit('/', 1)[-1]
	for input_file_p in args.input_files_with_p:
		df = refine_df(
			input_file_p,
			args.is_append_refined_text)
		save_df(
			df,
			args.path,
			output_file_f(input_file_p),
			args.is_leave_refined_texts_only)


if __name__ == '__main__':
	main()
