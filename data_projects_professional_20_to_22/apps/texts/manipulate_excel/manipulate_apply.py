from datetime import datetime
from functools import reduce
import re
import regex

import pandas as pd

from libs.utils.df_utils import DFUtils
from libs.utils.similarity_calculator import SimilarityCalculator
from libs.utils.text_utils import TextUtils


app_name = 'manipulate_apply'
lang_codes = ['ar', 'de', 'en', 'es', 'fr', 'hi', 'id', 'ja', 'ko', 'ms', 'ne', 'pt', 'ru', 'th', 'tl', 'tr', 'vi', 'zh']
now_s = lambda: str(datetime.now())


def get_keywords_freq_series(df, col_name, path, keywords_file=None, keywords=None, is_exact_keyword_matching=False, is_start_with_keyword=False):
	if keywords_file:
		with open(f'{path}/{keywords_file}') as f:
			keywords = [line.strip() for line in f.readlines()]

	if isinstance(keywords, str):
		keywords = [keywords]

	if keywords:
		if is_start_with_keyword:
			matched_keywords_count_f = lambda text: len([keyword for keyword in keywords if text.lower().startswith(keyword.lower())])
			freq_series = df[col_name].apply(matched_keywords_count_f)
		else:
			if is_exact_keyword_matching:
				case_insensitive_f = lambda x, y: (x if isinstance(x, str) else str(x)).lower() == (y if isinstance(y, str) else str(y)).lower()
			else:
				case_insensitive_f = lambda x, y: (x if isinstance(x, str) else str(x)).lower() in (y if isinstance(y, str) else str(y)).lower()
			freq_series = df[col_name].apply(lambda text: len([keyword for keyword in keywords if case_insensitive_f(keyword, text)]))
	else:
		freq_series = pd.DataFrame(data=[0] * len(df))

	return freq_series


def drop_by_keywords(df, args):
	keywords_freq_series = get_keywords_freq_series(
		df,
		args.check_col_name,
		args.path,
		args.keywords_file,
		args.keywords,
		args.is_exact_keyword_matching,
		args.is_start_with_keyword)

	if args.is_add_keywords_freq:
		df[f'freq_{args.check_col_name}'] = keywords_freq_series

	if args.is_drop_keywords:
		drop_filter_f = lambda x: x > 0
	else:
		drop_filter_f = lambda x: x <= 0
	dropped_df = df[keywords_freq_series.apply(drop_filter_f)]

	output_file = f'_dropped.'.join(args.output_file.rsplit('.', 1))
	df_utils = DFUtils('df_utils')
	df_utils.save(
		dropped_df,
		args.path,
		output_file)

	df = df[~keywords_freq_series.apply(drop_filter_f)]

	return df


def drop_by_empty(df, args):
	if args.is_drop_empty:
		dropped_series = df[args.check_col_name].isnull()
	else:
		dropped_series = ~df[args.check_col_name].isnull()

	output_file = f'_dropped.'.join(args.output_file.rsplit('.', 1))
	df_utils = DFUtils('df_utils')
	df_utils.save(
		df[dropped_series],
		args.path,
		output_file)

	if args.is_drop_empty:
		df = df[~dropped_series]
	else:
		df = df[dropped_series]

	return df


def get_value_filter(args):
	words_count = lambda col: len(col.split(' '))
	chars_count = lambda col: len(col)

	value_filter = None
	if args.leave_ko:
		value_filter = lambda col: bool(re.compile('[ㄱ-ㅎㅏ-ㅣ가-힣]+').findall(col))
	elif args.min_words_count > 0 and args.max_words_count > 0:
		value_filter = lambda col: args.min_words_count <= words_count(col) <= args.max_words_count
	elif args.min_chars_count > 0 and args.max_chars_count > 0:
		value_filter = lambda col: args.min_chars_count <= chars_count(col) <= args.max_chars_count
	elif args.min_words_count > 0:
		value_filter = lambda col: words_count(col) >= args.min_words_count
	elif args.max_words_count > 0:
		value_filter = lambda col: words_count(col) <= args.max_words_count
	elif args.min_chars_count > 0:
		value_filter = lambda col: chars_count(col) >= args.min_chars_count
	elif args.max_chars_count > 0:
		value_filter = lambda col: chars_count(col) <= args.max_chars_count

	return value_filter


def add_length(df):
	text_utils = TextUtils('text_utils')
	lang_col_names = [col_name for col_name in list(df.columns) if col_name in lang_codes]
	for lang_code in lang_col_names:
		print('{} [INFO][{}.add_length] Adding length for {} ...'.format(now_s(), app_name, lang_code))
		len_col_name = f'len_{lang_code}'
		df[len_col_name] = text_utils.get_lengths(lang_code, df[lang_code])
		print('{} [INFO][{}.add_length] sum: {:,}, mean: {} for {}'.format(now_s(), app_name, df[len_col_name].sum(), df[len_col_name].mean(), lang_code))


def drop_by_length_ratio(df, col_name1, col_name2, max_len_ratio):
	print('{} [INFO][{}.drop_by_length_ratio] Dropping by length ratio for {} and {} ...'.format(now_s(), app_name, col_name1, col_name2))

	all_len_df = len(df)
	words_count_f = lambda text: len(text.split(' '))
	chars_count_f = lambda text: len(text)
	ja_pattern = regex.compile(r'([\p{IsHan}\p{IsBopo}\p{IsHira}\p{IsKatakana}]+)', regex.UNICODE)
	zh_pattern = re.compile(r'[\u4e00-\u9fff]+')
	ja_chars_count_f = lambda text: reduce(lambda x, y: x + y, list(map(lambda x: len(x), ja_pattern.findall(text))))
	zh_chars_count_f = lambda text: reduce(lambda x, y: x + y, list(map(lambda x: len(x), zh_pattern.findall(text))))
	length_f = lambda lang_code: words_count_f if lang_code in ['de', 'en', 'es', 'fr', 'id', 'it', 'ko', 'ms', 'pt', 'ru', 'tl', 'tr', 'vi'] else ja_chars_count_f if lang_code == 'ja' else zh_chars_count_f if lang_code == 'zh' else chars_count_f

	length_ratio_f = lambda x, y, f1, f2: f1(x) / f2(y)
	length_filter_f = lambda x: 1/max_len_ratio <= x <= max_len_ratio
	df[f'{col_name1}_len'] = df[col_name1].apply(length_f(col_name1))
	df[f'{col_name2}_len'] = df[col_name2].apply(length_f(col_name2))
	df['len_ratio'] = df.apply(lambda cols: length_ratio_f(cols[col_name1], cols[col_name2], length_f(col_name1), length_f(col_name2)), axis=1)
	df = df[df.apply(lambda cols: length_ratio_f(cols[col_name1], cols[col_name2], length_f(col_name1), length_f(col_name2)), axis=1).apply(length_filter_f)]

	print('{} [INFO][{}.drop_by_length_ratio] {:,} rows dropped and {:,} rows alived in {:,} rows'.format(now_s(), app_name, all_len_df - len(df), len(df), all_len_df))
	return df


def apply_df(df, args):
	print('{} [INFO][{}.apply_df] Applying filters ...'.format(now_s(), app_name))

	before_len_df = len(df)
	is_in_f = lambda col_name: col_name in list(df.columns)

	if args.is_add_len:
		add_length(df)

	if args.add_col_names and args.add_col_values and len(args.add_col_names) == len(args.add_col_values):
		cols_i, cols_count = 0, len(args.add_col_names)
		for col_name, col_value in zip(args.add_col_names, args.add_col_values):
			cols_i += 1
			print('{} [INFO][{}.apply_df][{}/{}] Adding new column {} with {} ...'.format(now_s(), app_name, cols_i, cols_count, col_name, col_value))
			df[col_name] = [col_value] * len(df)

	if args.sim_col_names and len(args.sim_col_names) >= 2 and all([is_in_f(col_name) for col_name in args.sim_col_names]):
		similarity_calculator = SimilarityCalculator('similarity_calculator', df)
		similarity_calculator.calc_two_cols(args.sim_col_names[0], args.sim_col_names[1])

	if args.comp_len_col_names and len(args.comp_len_col_names) >= 2 and all([is_in_f(col_name) for col_name in args.comp_len_col_names]):
		df = drop_by_length_ratio(
			df,
			args.comp_len_col_names[0],
			args.comp_len_col_names[1],
			args.max_len_ratio)

	if (args.is_drop_keywords or args.is_drop_except_keywords) and (args.keywords or args.keywords_file) and is_in_f(args.check_col_name):
		df = drop_by_keywords(df, args)
	elif (args.is_drop_empty or args.is_drop_not_empty) and is_in_f(args.check_col_name):
		df = drop_by_empty(df, args)
	elif args.replace_from and is_in_f(args.check_col_name):
		df[args.check_col_name] = df[args.check_col_name].apply(lambda text: text.replace(args.replace_from, args.replace_to) if isinstance(text, str) else text)
	else:
		value_filter = get_value_filter(args)
		if value_filter:
			df = df[df[args.check_col_name].apply(value_filter)]

		if args.is_include_uppercase and is_in_f(args.check_col_name):
			re_en = re.compile('[a-zA-Z]+')
			is_include_all_uppercase_word_f = lambda text: len([1 for x, y in zip([x for x in re_en.findall(text) if len(x) > 1], [x for x in re_en.findall(text.upper()) if len(x) > 1]) if x == y])
			df[f'uppercase_{args.check_col_name}'] = df[args.check_col_name].apply(is_include_all_uppercase_word_f)

	if (dropped_count := before_len_df - len(df)) == 0:
		message = 'Nothing dropped'
	else:
		message = '{:,} rows dropped and {:,} rows alived in {:,} rows'.format(dropped_count, len(df), before_len_df)
	print('{} [INFO][{}.apply_df] {} by filters'.format(now_s(), app_name, message))
	return df


# def check_grammar_df(df, check_col_name):
# 	corrected_count = 0
# 	rows = []
# 
# 	grammar_checker = GrammarChecker('grammar_checker')
# 	for row in df[check_col_name].values:
# 		corrected_texts = grammar_checker.correct(row)
# 		if corrected_texts:
# 			corrected_count += 1
# 			rows += ['\n'.join(corrected_texts)]
# 		else:
# 			rows += ['']
# 
# 	df.insert(len(df.columns), f'corrected_{check_col_name}', rows)
# 	print('{} [INFO][{}.check_grammar_df] {:,} rows corrected'.format(now_s(), app_name, corrected_count))
# 	return df
