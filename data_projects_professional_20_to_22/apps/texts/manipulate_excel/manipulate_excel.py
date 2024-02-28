#!../../../bin/python3

'''
#
# df_a & df_b
#
diff      | check_col_names | none (*)
intersect |                 | lang_penalty

#
# df
#
drop_dup     | check_col_names | none (*)       | none (*)
drop_dup_all |                 | check_each_col | lang_penalty
dup          |                 |

#
# df
#
sort | check_col_name | asc (default)
     |                | desc
'''

import warnings
warnings.filterwarnings(action='ignore') 

from datetime import datetime

from cmd_args_manipulate import CMDArgsManipulate
from config import Config
from libs.utils.alert import Alert
from libs.utils.reader import Reader
import manipulate_preprocess
import manipulate_apply
import manipulate_postprocess


app_name = 'manipulate_excel'
lang_codes = ['ar', 'de', 'en', 'es', 'fr', 'hi', 'id', 'ja', 'ko', 'ms', 'ne', 'pt', 'ru', 'th', 'tl', 'tr', 'vi', 'zh']
now_s = lambda: str(datetime.now())


def get_df(input_file_p, count, sheet_index, col_indices, col_names, start_row, is_add_cleaned_yn, lang_codes, is_masking_piis, is_remove_newline):
	print('{} [INFO][{}.get_df] Reading {} ...'.format(now_s(), app_name, input_file_p))

	reader = Reader('reader', lang_codes)
	valid_col_indices = [x for x in col_indices if x >= 0]
	df = reader.get_df(
		input_file_p,
		sheet_index,
		valid_col_indices,
		col_names,
		start_row,
		nrows=count,
		is_add_cleaned_yn=is_add_cleaned_yn,
		is_masking_piis=is_masking_piis,
		is_remove_newline=is_remove_newline)

	if len(col_indices) != len(valid_col_indices):
		padding_indices = [index for index, x in enumerate(col_indices) if x < 0]
		values = [0] * len(df)
		for index, padding_index in enumerate(padding_indices):
			col_name = 'padding_{}'.format(index + 1)
			df.insert(padding_index, col_name, values)

	print('{} [INFO][{}.get_df] {:,} rows fetched'.format(now_s(), app_name, len(df)))
	return df


def notify(level, message, is_noti_to_slack):
	level = level.upper()
	print('%s [%s]%s' % (now_s(), level, message))
	if is_noti_to_slack:
		alert.send(level, '`[%s]` %s' % (level, message))


def main():
	args_manipulate = CMDArgsManipulate('cmd_args_manipulate_excel', ['path'])
	args = args_manipulate.values

	global config
	config = Config('config', is_dev=not args.is_production)

	if args.is_noti_to_slack:
		global alert
		alert = Alert('alert')

	df = None
	dfs = []
	for input_file_p in args.input_files_p:
		dfs += [get_df(input_file_p,
			args.count,
			args.sheet_index,
			args.col_indices,
			args.col_names,
			args.start_row,
			args.is_add_cleaned_yn,
			lang_codes,
			args.is_masking_piis,
			args.is_remove_newline)]

	df = manipulate_preprocess.preprocess_dfs(dfs, args)
	df = manipulate_apply.apply_df(df, args)
	manipulate_postprocess.postprocess_df(df, args)


if __name__ == '__main__':
	main()
