#!../../../bin/python3

from datetime import datetime
import time

import pandas as pd

from cmd_args_translate import CMDArgsTranslate
from config import Config
from libs.utils.alert import Alert
from libs.utils.df_utils import DFUtils
from libs.utils.mt import MT
from libs.utils.mt_baidu import MTBaidu
from libs.utils.mt_direct import MTDirect
from libs.utils.mt_ibm import MTIBM
from libs.utils.mt_textra import MTTextra, MTTextra2, MTTextra3
from libs.utils.reader import Reader


app_name = 'translate'
output_filename_f = lambda base_name, kind: f'_{kind}.'.join(base_name.rsplit('.', 1))
split_filename_f = lambda base_name: (*(base_name.rsplit('/', 1)), base_name.rsplit('.', 1)[-1].lower())


def get_df(input_file_p):
	print('{} [INFO][{}.get_df] Reading {} ...'.format(str(datetime.now()), app_name, input_file_p))

	reader = Reader('reader')
	df = reader.get_simple_df(input_file_p)

	print('{} [INFO][{}.get_df] {:,} rows fetched'.format(str(datetime.now()), app_name, len(df)))
	return df


def translate_df(df, mts, src_lang_code, dst_lang_code, rows_count_per_call, threshold_count, sleep_secs, is_verbose):
	mt = mts[0]
	df_utils = DFUtils('df_utils')
	dfs = df_utils.slice(df, rows_count_per_call)

	is_over_threshold_count = False
	failed_mts_count = 0
	continuous_fails_count = 0
	all_trs = []
	count = 0
	all_count = sum([len(df) for df in dfs])
	for sliced_df in dfs:
		count += 1
		# texts = '\n'.join(sliced_df[src_lang_code])
		texts = '\n'.join(map(lambda x: str(x), sliced_df[src_lang_code]))
		trs = mt.send(src_lang_code, dst_lang_code, texts).split('\n')

		if is_verbose:
			print('{} [INFO][{}.translate_df][{}/{}] {} --> {}'.format(str(datetime.now()), app_name, count, all_count, src_lang_code, texts if len(texts) > 0 else ''))
			print('{} [INFO][{}.translate_df][{}/{}] {} <-- {}'.format(str(datetime.now()), app_name, count, all_count, dst_lang_code, trs[0] if len(trs) > 0 else ''))

		if rows_count_per_call == len(trs) and all([len(tr) > 0 for tr in trs]):
			all_trs += [*trs]
			continuous_fails_count = 0
		else:
			all_trs += [*([''] * rows_count_per_call)]
			continuous_fails_count += 1

		if continuous_fails_count > threshold_count:
			message = '[{}.translate_df] Continuous fails count is over {}! ({} -> {})'.format(app_name, threshold_count, src_lang_code, dst_lang_code)
			notify('critical', message, True)

			if len(mts) > 1 and failed_mts_count < len(mts)-1:
				failed_mts_count += 1
				continuous_fails_count = 0
				mts = [*mts[1:], mts[0]]
				mt = mts[0]
				time.sleep(600)
			else:
				is_over_threshold_count = True
				break
		elif sleep_secs > 0:
			time.sleep(sleep_secs)

	if is_over_threshold_count and (remainder := len(df)-len(all_trs)) > 0:
		all_trs += [*([''] * remainder)]

	mt_col_name = f'mt_{dst_lang_code}'
	df.insert(len(df.columns), mt_col_name, all_trs)
	all_failed_count = len(df[df[mt_col_name] == ''])
	print('{} [INFO][{}.translate_df] {:,} rows translated and {:,} rows not translated'.format(str(datetime.now()), app_name, len(df)-all_failed_count, all_failed_count))

	return is_over_threshold_count, mts


def translate(df, config, path, output_file, mt_type, src_lang_code, dst_lang_code, rows_count_per_iter, rows_count_per_call, threshold_count, sleep_secs, is_verbose):
	mts = []
	if mt_type == 'baidu':
		mts += [MTBaidu('mt_baidu', config)]
	elif mt_type == 'direct':
		mts += [MTDirect('mt_direct', config)]
	elif mt_type == 'ibm':
		mts += [MTIBM('mt_ibm', config)]
	elif mt_type == 'textra':
		mts += [MTTextra('mt_textra', config)]
		mts += [MTTextra2('mt_textra2', config)]
		mts += [MTTextra3('mt_textra3', config)]
	else:
		mts += [MT('mt', config)]

	df_utils = DFUtils('df_utils')
	dfs = df_utils.slice(df, rows_count_per_iter)

	for i, sliced_df in enumerate(dfs):
		print('{} [INFO][{}.translate_df][{}/{}] Translating {:,} texts ...'.format(str(datetime.now()), app_name, i+1, len(dfs), len(sliced_df)))
		is_over_threshold_count, mts = translate_df(
			sliced_df,
			mts,
			src_lang_code,
			dst_lang_code,
			rows_count_per_call,
			threshold_count,
			sleep_secs,
			is_verbose)
		iter_output_file = output_filename_f(output_file, i+1)
		df_utils.save(sliced_df, path, iter_output_file)

		if is_over_threshold_count:
			break


def notify(level, message, is_noti_to_slack):
	level = level.upper()
	print('%s [%s]%s' % (str(datetime.now()), level, message))
	if is_noti_to_slack:
		alert.send(level, '`[%s]` %s' % (level, message))


def main():
	args_translate = CMDArgsTranslate('translate', ['path', 'input_files', 'output_file', 'mt_lang_codes'])
	args = args_translate.values

	global config
	config = Config('config', is_dev=not args.is_production)

	if args.is_noti_to_slack:
		global alert
		alert = Alert('alert')

	dfs = []
	for input_file_p in args.input_files_with_p:
		dfs += [get_df(input_file_p)]

	df_utils = DFUtils('df_utils')
	df = df_utils.concat_v(dfs)

	translate(
		df,
		config,
		args.path,
		args.output_file,
		args.mt_type,
		args.mt_lang_codes[0],
		args.mt_lang_codes[1],
		args.rows_count_per_iter,
		args.rows_count_per_call,
		args.threshold_count,
		args.sleep_secs,
		args.is_verbose)

	message = '[{}.main] All translations are complete for {}!'.format(app_name, args.input_files_with_p[0])
	notify('info', message, args.is_noti_to_slack)


if __name__ == '__main__':
	main()
