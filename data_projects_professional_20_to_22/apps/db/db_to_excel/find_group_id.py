#!../../../bin/python3

#
# NOTE : 테스트용
#
import pandas as pd

from cmd_args_find import CMDArgsFind
from config import Config
from libs.utils.db import DB
from libs.utils.df_utils import DFUtils


app_name = 'find_group_id'


def find_group_ids(db, df, col_i):
	sql = f' \
		SELECT group_id \
		FROM parallel_corpus \
		WHERE corpus_id = %s \
		ORDER BY group_id DESC \
		LIMIT 1 \
	'

	group_ids = []
	for _, row in df.iterrows():
		values = [row[col_i]]
		fetched_row = db.fetch_row(sql, values)
		group_id = fetched_row[0] if fetched_row else ''
		group_ids += [group_id]
		print(f'group_id: {group_id}')

	df.insert(len(df.columns), 'group_id', group_ids)


def main():
	args_find = CMDArgsFind('args', [])
	args = args_find.values

	config = Config('config', is_dev=not args.is_production)
	if not config.is_loaded:
		print(f'[CRITICAL][{app_name}.main] Can\'t open config.ini.')
		return

	db = DB('db', config)
	db.open()

	df = pd.read_excel(args.input_files_with_p[0])
	find_group_ids(db, df, args.corpus_col_i)

	db.close()

	df_utils = DFUtils('df_utils')
	df_utils.save(df, args.path, args.output_file)


if __name__ == '__main__':
	main()
