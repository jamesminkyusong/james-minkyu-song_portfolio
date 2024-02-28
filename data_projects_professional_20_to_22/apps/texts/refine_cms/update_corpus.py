#!../../../bin/python3

"""
Purpose
-------
Update cleaned corpora in DB and ES

Steps
-----
1. Read mono_LANG_clean_only_[0-9]*.xlsx
   Sample rows of this file are like below:
   sid | group_id | fr_id   | fr                              | fr_source            | tag | fr_cleaned
   ----+----------+---------+---------------------------------+----------------------+-----+-----------
   2   | 8651072  | 7497049 | C'est super.                    | 2017_ETRI_영독프러스 | nan | Y
   3   | 8558623  | 7476621 | Combien coûte un ticket de bus? | 2017_ETRI_영독프러스 | nan | Y
2. Update these in DB and ES
"""

from datetime import datetime

from config import Config
from libs.corpus.corpus import Corpus
from libs.utils.alert import Alert
from libs.utils.cmd_args import CMDArgs
from libs.utils.db import DB
from libs.utils.df_utils import DFUtils
from libs.utils.es import ES
from libs.utils.reader import Reader


def get_df(path, input_file, col_indices, col_names, start_row, lang_codes):
	print('{} [INFO][cleaning_corpus.get_df] Reading from {} ...'.format(str(datetime.now()), input_file))

	reader = Reader('reader', lang_codes)
	df = reader.get_df('%s/%s' % (path, input_file), 0, col_indices, col_names, start_row)

	print('{} [INFO][cleaning_corpus.get_df] {:,} rows fetched'.format(str(datetime.now()), len(df)))
	return df


def update_db_and_es(df, db, es, lang_code):
	corpus = Corpus('corpus', db=db)
	for index, row in enumerate(df.values):
		corpus_id = int(row[0])
		text = row[1]

		corpus.update_text(corpus_id, text)
		es.insert(lang_code, corpus_id, text)
		if (h_index := index + 1) % 1000 == 0:
			print('{} [INFO][cleaning_corpus.update_db_and_es] {:,} rows refined'.format(str(datetime.now()), h_index))


def notify(level, message, is_noti_to_slack):
	level = level.upper()
	print('%s [%s]%s' % (str(datetime.now()), level, message))
	if is_noti_to_slack:
		alert.send(level, '`[%s]` %s' % (level, message))


def main():
	args_refine = CMDArgs('cmd_args_refine', ['path', 'col_indices', 'col_names'])
	args = args_refine.values

	global config
	config = Config('config')

	if args.is_noti_to_slack:
		global alert
		alert = Alert('alert')

	db = DB('db', config)
	db.open()

	es = ES('es', config.es_host)
	if not es.is_connected:
		print('[CRITICAL][cleaning_corpus.main] Can\'t connect to ElasticSearch.')
		return

	langs = db.fetch_languages()
	lang_codes = langs.keys()

	dfs = []
	for input_file in args.input_files:
		dfs += [get_df(args.path, input_file, args.col_indices, args.col_names, args.start_row, lang_codes)]
	df_utils = DFUtils('df_utils')
	df = df_utils.merge(dfs)

	lang_col_name = list(set(args.col_names) & set(lang_codes))[0]
	update_db_and_es(df, db, es, lang_col_name)
	message = '[cleaning_corpus.main] {:,} rows updated in {}'.format(len(df), str(args.input_files))
	notify('info', message, args.is_noti_to_slack)

	db.close()


if __name__ == '__main__':
	main()
