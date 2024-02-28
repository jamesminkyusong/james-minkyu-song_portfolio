from datetime import datetime

import pandas as pd

from libs.utils.df_utils import DFUtils


app_name = 'manipulate_preprocess'
now_s = lambda: str(datetime.now())


def diff_and_intersect_df(dfs, col_names, is_lang_penalty, is_ignore_case, path, input_files, output_file, is_save_diff, is_save_intersect):
	print('{} [INFO][{}.diff_and_intersect_df] Diff and intersect by {} ...'.format(now_s(), app_name, col_names))

	df_utils = DFUtils('df_utils')
	output_file_f = lambda filename, kind: f'_{kind}.'.join(filename.rsplit('.', 1))

	if len(dfs) == 2:
		diff_df, intersect_df = df_utils.diff_and_intersect(
			dfs[0],
			dfs[1],
			col_names,
			is_lang_penalty=is_lang_penalty,
			is_ignore_case=is_ignore_case)
	else:
		diff_df, intersect_df = dfs[0], dfs[0]
		for df_i, df in enumerate(dfs[1:]):
			print('{} [INFO][{}.diff_and_intersect_df] Diff and intersect between {} and {} ...'.format(now_s(), app_name, input_files[0], input_files[df_i+1]))
			diff_df, _ = df_utils.diff_and_intersect(
				diff_df,
				df,
				col_names,
				is_lang_penalty=is_lang_penalty,
				is_ignore_case=is_ignore_case)
			_, intersect_df = df_utils.diff_and_intersect(
				intersect_df,
				df,
				col_names,
				is_lang_penalty=is_lang_penalty,
				is_ignore_case=is_ignore_case)

	if is_save_diff:
		df_utils.save(
			diff_df,
			path,
			output_file_f(output_file, 'diff'),
			is_save_empty_df=False)

	if is_save_intersect:
		df_utils.save(
			intersect_df,
			path,
			output_file_f(output_file, 'intersect'),
			is_save_empty_df=False)

	return diff_df


def drop_duplicates(df, col_names, is_keep_first, is_lang_penalty, is_ignore_case, is_check_each_col, path, output_file):
	print('{} [INFO][{}.drop_duplicates] Drop duplicates by {} ...'.format(now_s(), app_name, col_names))

	df_utils = DFUtils('df_utils')
	output_file_f = lambda keyword: ('_{}_{}.'.format(keyword, '_'.join(col_names))).join(output_file.rsplit('.', 1))

	df, dup_df, dropped_df = df_utils.drop_duplicates(
		df,
		col_names,
		is_keep_first=is_keep_first,
		is_lang_penalty=is_lang_penalty,
		is_ignore_case=is_ignore_case,
		is_check_each_col=is_check_each_col)

	df_utils.save(
		dup_df,
		path,
		output_file_f('dup'),
		is_save_empty_df=False)

	df_utils.save(
		dropped_df,
		path,
		output_file_f('dropped'),
		is_save_empty_df=False)

	return df


def drop_almost_duplicates(df, col_names, is_lang_penalty, is_show_almost_dup_as_vertical, path, output_file):
	print('{} [INFO][{}.drop_almost_duplicates] Drop almost duplicates by {} ...'.format(now_s(), app_name, col_names))

	df_utils = DFUtils('df_utils')
	output_file_f = lambda keyword: ('_{}_{}.'.format(keyword, '_'.join(col_names))).join(output_file.rsplit('.', 1))

	df, similar_df = df_utils.drop_almost_duplicates(
		df,
		col_names,
		is_lang_penalty=is_lang_penalty,
		is_show_almost_dup_as_vertical=is_show_almost_dup_as_vertical)

	df_utils.save(
		similar_df,
		path,
		output_file_f('almost_dup_dropped'),
		is_save_empty_df=False)

	return df


def drop_duplicates_all(df, col_names, is_lang_penalty, is_ignore_case, path, output_file):
	print('{} [INFO][{}.drop_duplicates_all] Drop all duplicates by {} ...'.format(now_s(), app_name, col_names))

	df_utils = DFUtils('df_utils')
	output_file_f = lambda keyword: ('_{}_{}.'.format(keyword, '_'.join(col_names))).join(output_file.rsplit('.', 1))

	df, dropped_df = df_utils.drop_duplicates_all(
		df,
		col_names,
		is_lang_penalty=is_lang_penalty,
		is_ignore_case=is_ignore_case)

	df_utils.save(
		dropped_df,
		path,
		output_file_f('dropped'),
		is_save_empty_df=False)

	return df


def get_duplicates_all(df, col_names, is_lang_penalty, is_ignore_case, is_check_each_col, path, output_file):
	df_utils = DFUtils('df_utils')
	output_file_f = lambda col_names: ('_dup_{}.'.format('_'.join(col_names))).join(output_file.rsplit('.', 1))

	if len(col_names) > 1 and is_check_each_col:
		dup_all_df = None
		for col_name in col_names:
			output_file = output_file_f([col_name])
			dup_df = df_utils.get_duplicates(
				df,
				col_names=[col_name],
				is_lang_penalty=is_lang_penalty,
				is_ignore_case=is_ignore_case)
			df_utils.save(
				dup_df,
				path,
				output_file,
				is_save_empty_df=False)
			if dup_all_df:
				dup_all_df = pd.concat([dup_all_df, dup_df])
				dup_all_df.drop_duplicates(subset=[col_names], keep='first', inplace=True)
			else:
				dup_all_df = dup_df
	else:
		output_file = output_file_f(col_names)
		dup_all_df = df_utils.get_duplicates(
			df,
			col_names=col_names,
			is_lang_penalty=is_lang_penalty,
			is_ignore_case=is_ignore_case)
		df_utils.save(
			dup_all_df,
			path,
			output_file,
			is_save_empty_df=False)

	return dup_all_df


def preprocess_dfs(dfs, args):
	df_utils = DFUtils('df_utils')
	if args.is_hcat:
		result_df = df_utils.concat_h(dfs) if len(dfs) > 1 else dfs[0]
	elif args.is_diff_and_intersect or args.is_diff or args.is_intersect:
		result_df = diff_and_intersect_df(
			dfs,
			args.check_col_names,
			args.is_lang_penalty,
			args.is_ignore_case,
			args.path,
			args.input_files,
			args.output_file,
			args.is_diff_and_intersect or args.is_diff,
			args.is_diff_and_intersect or args.is_intersect)
	else:
		result_df = df_utils.concat_v(dfs) if len(dfs) > 1 else dfs[0]
		if args.is_drop_dup and args.check_col_names:
			result_df = drop_duplicates(
				result_df,
				args.check_col_names,
				args.is_keep_first,
				args.is_lang_penalty,
				args.is_ignore_case,
				args.is_check_each_col,
				args.path,
				args.output_file)
		elif args.is_drop_almost_dup and args.check_col_names:
			result_df = drop_almost_duplicates(
				result_df,
				args.check_col_names,
				args.is_lang_penalty,
				args.is_show_almost_dup_as_vertical,
				args.path,
				args.output_file)
		elif args.is_drop_dup_all and args.check_col_names:
			result_df = drop_duplicates_all(
				result_df,
				args.check_col_names,
				args.is_lang_penalty,
				args.is_ignore_case,
				args.path,
				args.output_file)
		elif args.is_dup and args.check_col_names:
			result_df = get_duplicates_all(
				result_df,
				args.check_col_names,
				args.is_lang_penalty,
				args.is_ignore_case,
				args.is_check_each_col,
				args.path,
				args.output_file)

	return result_df
