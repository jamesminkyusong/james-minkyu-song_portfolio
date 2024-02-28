#!../../../bin/python3

"""
Purpose
-------
Find duplicated rows and delete these in DB

Steps
-----
1. Read mono_LANG_[0-9]*.xlsx
2. Created dup_mono_LANG.xlsx which has duplicated corpora in DB
   Sample rows of this file are like below:
   sid | group_id_x | LANG_id_x | LANG                 | group_id_y | LANG_id_y
   ----+------------+-----------+----------------------+------------+----------
   1   | 3492721    | 2254364   | Où est-ce?           | 3398935    | 7477524
   2   | 3492709    | 11724518  | Où est-ce situé?     | 623081     | 7504635
   3   | 3443562    | 11731728  | Où puis-je le faire? | 628446     | 7479487
3. Move each row which language is not in a newer group to new groups and delete old groups
"""

from datetime import datetime

import pandas as pd

from cmd_args_merge import CMDArgsMerge
from config import Config
from libs.corpus.parallel_corpus import ParallelCorpus
from libs.utils.alert import Alert
from libs.utils.db import DB
from libs.utils.df_utils import DFUtils
from libs.utils.reader import Reader


app_name = 'merge_groups'
lang_codes = ['ar', 'de', 'en', 'es', 'fr', 'hi', 'id', 'ja', 'ko', 'ms', 'ne', 'pt', 'ru', 'th', 'tl', 'tr', 'vi', 'zh']
now_s = lambda: str(datetime.now())


def get_df(input_file_p):
	print('{} [INFO][{}.get_df] Reading {} ...'.format(now_s(), app_name, input_file_p))
	df = pd.read_excel(input_file_p)

	print('{} [INFO][{}.get_df] {:,} rows fetched'.format(now_s(), app_name, len(df)))
	return df


def get_mono_df(input_files_p, col_indices):
	dfs = []
	for input_file_p in input_files_p:
		print('{} [INFO][{}.get_df] Reading {} ...'.format(now_s(), app_name, input_file_p))
		df = pd.read_excel(input_file_p, usecols=col_indices)
		dfs += [df]
		print('{} [INFO][{}.get_df] {:,} rows fetched'.format(now_s(), app_name, len(df)))

	df_utils = DFUtils('df_utils')
	all_df = df_utils.concat_v(dfs)

	print('{} [INFO][{}.get_df] All {:,} rows fetched'.format(now_s(), app_name, len(all_df)))
	return all_df


def get_dup_df(df, lang_code):
	print('{} [INFO][{}.get_dup_df] Searching duplicated texts for {} ...'.format(now_s(), app_name, lang_code))
	first_dup_df = df[~df.duplicated(subset=lang_code, keep='first')]
	remainders_dup_df = df[df.duplicated(subset=lang_code, keep='first')]
	dup_df = pd.merge(first_dup_df, remainders_dup_df, on=[lang_code])

	print('{} [INFO][{}.get_dup_df] {:,} rows dupped'.format(now_s(), app_name, len(dup_df)))
	return dup_df


def update_corpus_db(df, db):
	parallel_corpus = ParallelCorpus('parallel_corpus', db)
	for index, row in enumerate(df.values):
		new_group_id = int(row[1])
		current_group_id = int(row[4])

		parallel_corpus.delete_duplicated_corpus(current_group_id, new_group_id)
		parallel_corpus.update_group_id(new_group_id, current_group_id)
		if (h_index := index + 1) % 1_000 == 0:
			print('{} [INFO][{}.update_corpus_db] {:,} rows refined'.format(now_s(), app_name, h_index))


def notify(level, message, is_noti_to_slack):
	level = level.upper()
	print('%s [%s]%s' % (str(datetime.now()), level, message))
	if is_noti_to_slack:
		alert.send(level, '`[%s]` %s' % (level, message))


def main():
	args_merge = CMDArgsMerge('merge_groups', ['lang_code'])
	args = args_merge.values

	global config
	config = Config('config', is_dev=not args.is_production)

	if args.is_noti_to_slack:
		global alert
		alert = Alert('alert')

	if args.dup_file:
		dup_df = get_df('{}/{}'.format(args.path, args.dup_file))
	else:
		df = get_mono_df(args.input_files_with_p, args.col_indices)
		dup_df = get_dup_df(df, args.lang_code)
		df_utils = DFUtils('df_utils')
		df_utils.add_sid(dup_df)
		df_utils.save(dup_df, args.path, args.output_file)

	if args.is_update_db:
		db = DB('db', config)
		db.open()
		update_corpus_db(dup_df, db)
		db.close()

	message = f'[{app_name}.main] Execution complete!'
	notify('info', message, args.is_noti_to_slack)


if __name__ == '__main__':
	main()
