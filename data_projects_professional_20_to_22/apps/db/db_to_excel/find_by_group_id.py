#!../../../bin/python3

#
# NOTE : 테스트용
#
import pandas as pd

from cmd_args_db import CMDArgsDB
from config import Config
from libs.utils.db import DB


app_name = 'find_by_group_id'


def main():
	args_db = CMDArgsDB('args', [])
	args = args_db.values

	config = Config('config', is_dev=not args.is_production)
	if not config.is_loaded:
		print(f'[CRITICAL][{app_name}.main] Can\'t open config.ini.')
		return

	df = pd.read_excel(args.input_files_with_p[0])

	db = DB('db', config)
	db.open()

	sql = f' \
		SELECT text \
		FROM corpus \
		WHERE id = (SELECT corpus_id \
			FROM parallel_corpus \
			WHERE group_id = %s \
				AND lang_id = 17 \
			ORDER BY corpus_id DESC \
			LIMIT 1) \
	'

	en_texts = []
	for _, row in df.iterrows():
		values = [row[1]]
		fetched_row = db.fetch_row(sql, values)
		en = fetched_row[0] if fetched_row else ''
		en_texts += [en]
		print(f'en: {en}')

	db.close()

	df.insert(len(df.columns), 'en', en_texts)
	df.to_excel(
		'%s/%s' % (args.path, args.output_file),
		index=False,
		engine='xlsxwriter')


if __name__ == '__main__':
	main()
