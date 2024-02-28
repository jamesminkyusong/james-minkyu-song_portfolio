#!../../../bin/python3

from datetime import datetime

from cmd_args_quality import CMDArgsQuality
from config import Config
from libs.quality_filter.quality_filter import QualityFilter
from libs.utils.alert import Alert
from libs.utils.df_utils import DFUtils
from libs.utils.reader import Reader


def get_df(path, count, input_file, sheet_index, col_indices, col_names, start_row, lang_codes, is_masking_piis):
	print('{} [INFO][check_quality.get_df] Reading {} ...'.format(str(datetime.now()), input_file))

	reader = Reader('reader', lang_codes)
	df = reader.get_df(
		'%s/%s' % (path, input_file),
		sheet_index,
		col_indices,
		col_names,
		start_row,
		nrows=count,
		is_masking_piis=is_masking_piis)

	print('{} [INFO][check_quality.get_df] {:,} rows fetched'.format(str(datetime.now()), len(df)))
	return df


def check_quality(df, args, lang_codes):
	quality_filter = QualityFilter('quality_filter', lang_codes=lang_codes, filters=args.filters)
	not_bad_df, bad_df = quality_filter.execute(df, col_names=df.columns)

	for category_df, category in zip([not_bad_df, bad_df], ['not_bad', 'bad']):
		if len(category_df) > 0:
			quality_filter.save_df(
				category_df,
				category,
				args.path,
				args.max_rows_in_file,
				args.input_files[0])

	if args.filters.is_check_similarity:
		for lang_col_name in [col_name for col_name in df.columns if col_name in lang_codes]:
			quality_filter.save_similarity_df(
				df,
				lang_col_name,
				args.filters.similarity_sid_col_name,
				df.columns,
				args.path,
				args.max_rows_in_file,
				args.input_files[0])

	if len(args.mt_lang_codes) == 2:
		mt_df = quality_filter.translate_df(
			config,
			not_bad_df,
			args.mt_sample_ratio,
			args.mt_lang_codes[0],
			args.mt_lang_codes[1])
		output_file = f'_mt.'.join(args.input_files[0].rsplit('.', 1))
		df_utils = DFUtils('df_utils')
		df_utils.save(mt_df, args.path, output_file)


def notify(level, message, is_noti_to_slack):
	level = level.upper()
	print('%s [%s]%s' % (str(datetime.now()), level, message))
	if is_noti_to_slack:
		alert.send(level, '`[%s]` %s' % (level, message))


def main():
	args_quality = CMDArgsQuality('cmd_args_quality', ['path', 'input_files'])
	args = args_quality.values

	global config
	config = Config('config', is_dev=not args.is_production)

	if args.is_noti_to_slack:
		global alert
		alert = Alert('alert')

	lang_codes = ['ar', 'de', 'en', 'es', 'fr', 'hi', 'id', 'ja', 'ko', 'ms', 'ne', 'pt', 'ru', 'th', 'tl', 'tr', 'vi', 'zh']

	dfs = []
	for input_file in args.input_files:
		dfs += [get_df(
			args.path,
			args.count,
			input_file,
			args.sheet_index,
			args.col_indices,
			args.col_names,
			args.start_row,
			lang_codes,
			args.is_masking_piis)]

	df_utils = DFUtils('df_utils')
	df = df_utils.concat_v(dfs) if len(dfs) > 1 else dfs[0]

	if args.is_add_sid:
		df_utils.add_sid(df)

	check_quality(df, args, lang_codes)

	message = '[check_quality.main] Check quality completed for {}'.format(args.input_files[0])
	notify('info', message, args.is_noti_to_slack)


if __name__ == '__main__':
	main()
