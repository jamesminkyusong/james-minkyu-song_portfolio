import math

from libs.utils.df_utils import DFUtils


app_name = 'manipulate_postprocess'


def split_df(df, split_col_name):
	dfs = []

	keys = list(filter(lambda x: x == x, df[split_col_name].unique()))	# NaN 제거
	for key in keys:
		dfs += [df[df[split_col_name] == key]]

	if sum(df[split_col_name].isna()) > 0:
		keys += ["empty"]
		dfs += [df[df[split_col_name].isna()]]

	return keys, dfs


def postprocess_df(df, args):
	if args.is_split and args.check_col_name in list(df.columns):
		keys, dfs = split_df(df, args.check_col_name)
	else:
		dfs = [df]

	df_utils = DFUtils('df_utils')
	for df_i in range(len(dfs)):
		if args.is_shuffle:
			dfs[df_i] = df_utils.shuffle(dfs[df_i])
		elif args.is_sort and args.check_col_name in list(dfs[df_i].columns):
			dfs[df_i].sort_values(by=args.check_col_name, ascending=args.is_asc, inplace=True)
		if args.is_add_sid:
			df_utils.add_sid(dfs[df_i], args.start_sid)
		if len(dfs[df_i]) > args.count:
			dfs[df_i] = dfs[df_i].head(args.count)

	if len(dfs) >= 2:
		for key, df_a in zip(keys, dfs):
			output_file = f'_{key}.'.join(args.output_file.rsplit('.', 1))
			df_utils.save(
				df_a,
				args.path,
				output_file,
				args.not_divide_output,
				args.max_rows_in_file,
				args.rows_count_in_files,
				args.lang_format,
				args.is_add_header)
	else:
		df_utils.save(
			dfs[0],
			args.path,
			args.output_file,
			args.not_divide_output,
			args.max_rows_in_file,
			args.rows_count_in_files,
			args.lang_format,
			args.is_add_header)
