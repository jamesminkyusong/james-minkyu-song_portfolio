#!../../../bin/python3

from datetime import datetime
import math
import time

import numpy as np

from cmd_args_excel import CMDArgsExcel
from config import Config
from libs.corpus.corpus import Corpus
from libs.utils.alert import Alert
from libs.utils.db import DB
from libs.utils.es import ES
from libs.utils.reader import Reader


app_name = 'excel_to_db'


def get_df(path, input_file):
	print('{} [INFO][{}.get_df] Reading {} ...'.format(str(datetime.now()), app_name, input_file))

	reader = Reader('reader')
	df = reader.get_simple_df(f'{path}/{input_file}')

	print('{} [INFO][{}.get_df] {:,} rows fetched'.format(str(datetime.now()), app_name, len(df)))
	return df


def insert_tags(corpus, is_preview, group_ids, tag_ids):
	npint_to_int = lambda x: 0 if math.isnan(x) else np.uint32(x).item()

	for index, value in enumerate(zip(group_ids, tag_ids)):
		tag_id = npint_to_int(value[1])
		if tag_id <= 0:
			continue

		group_id = npint_to_int(value[0])
		if is_preview:
			print(f'group, tag: {group_id}, {tag_id}')
		else:
			corpus.insert_tag(group_id, tag_id)

		if (h_i := index+1) % 1_000 == 0 or h_i == len(group_ids):
			print('{} [INFO][{}.insert_tag] {:,} rows tagged'.format(str(datetime.now()), app_name, h_i))


def insert_mono_df(df, is_preview, lang_col_name, text_col_name, tag_col_name, langs, corpus):
	lang_i = list(df.columns).index(lang_col_name)
	text_i = list(df.columns).index(text_col_name)
	if tag_col_name:
		tag_i = list(df.columns).index(tag_col_name)
		tag_ids = []

	group_ids = []
	for index, row in enumerate(df.values):
		lang = row[lang_i]
		text = row[text_i]
		lang_id = langs[lang]

		if is_preview:
			print('texts #{:,}:'.format(index + 1))
			print('[{}/{}] {}'.format(lang, lang_id, text))
			if tag_col_name:
				print(f'tag: {row[tag_i]}')
		else:
			group_id = corpus.insert_mono(lang_id, text)
			if tag_col_name and group_id > 0:
				group_ids += [group_id]
				tag_ids += [row[tag_i]]

		if not is_preview and ((h_i := index+1) % 1_000 == 0 or h_i == len(df)):
			print('{} [INFO][{}.insert_mono_df] {:,} rows inserted'.format(str(datetime.now()), app_name, h_i))

	if tag_col_name:
		insert_tags(corpus, is_preview, group_ids, tag_ids)


def insert_df(df, is_preview, lang_col_names, text_col_names, tag_col_name, langs, corpus):
	lang1_i = list(df.columns).index(lang_col_names[0])
	lang2_i = list(df.columns).index(lang_col_names[1])
	text1_i = list(df.columns).index(text_col_names[0])
	text2_i = list(df.columns).index(text_col_names[1])
	if tag_col_name:
		tag_i = list(df.columns).index(tag_col_name)
		tag_ids = []

	group_ids = []
	for index, row in enumerate(df.values):
		lang1, lang2 = row[lang1_i], row[lang2_i]
		text1, text2 = row[text1_i], row[text2_i]
		lang1_id, lang2_id = langs[lang1], langs[lang2]

		if is_preview:
			print('texts #{:,}:'.format(index + 1))
			print('[{}/{}] {}'.format(lang1, lang1_id, text1))
			print('[{}/{}] {}'.format(lang2, lang2_id, text2))
			if tag_col_name:
				print(f'tag: {row[tag_i]}')
		else:
			group_id = corpus.insert(lang1_id, text1, lang2_id, text2)
			if tag_col_name and group_id > 0:
				group_ids += [group_id]
				tag_ids += [row[tag_i]]

		if not is_preview and ((h_i := index+1) % 1_000 == 0 or h_i == len(df)):
			print('{} [INFO][{}.insert_df] {:,} rows inserted'.format(str(datetime.now()), app_name, h_i))

	if tag_col_name:
		insert_tags(corpus, is_preview, group_ids, tag_ids)


def insert_df_with_group_and_tag(df, is_preview, lang_col_names, group_col_name, tag_col_name, corpus):
	npint_to_int = lambda x: 0 if math.isnan(x) else np.uint32(x).item()

	group_ids = df[group_col_name]
	for lang_id, lang_col_name in lang_col_names:
		for index, value in enumerate(zip(group_ids.values, df[lang_col_name].values)):
			group_id = npint_to_int(value[0])
			text = value[1]
			if is_preview:
				print(f'group_id, lang_id, text: {group_id}, {lang_id}, {text}')
			else:
				corpus.insert_with_group_id(group_id, lang_id, text)

			if (h_i := index+1) % 1_000 == 0 or h_i == len(df):
				print('{} [INFO][{}.insert_df_with_group_and_tag] {:,} rows inserted'.format(str(datetime.now()), app_name, h_i))

	if tag_col_name:
		insert_tags(corpus, is_preview, group_ids, df[tag_col_name])


def notify(level, message, is_noti_to_slack):
	level = level.upper()
	print('%s [%s]%s' % (str(datetime.now()), level, message))
	if is_noti_to_slack:
		alert.send(level, '`[%s]` %s' % (level, message))


def main():
	args_excel = CMDArgsExcel('cmd_args_excel', ['path', 'input_files'])
	args = args_excel.values

	config = Config('config', is_dev=not args.is_production)
	if not config.is_loaded:
		print('[CRITICAL][{}.main] Can\'t open config.ini.'.format(app_name))
		return

	if args.is_production:
		print(
			'===== ===== =====\n'
			'Warning!!!\n'
			'You\'re trying to insert into PRODUCTION DB and ES. Please STOP right now if you set wrong "--prod"\n'
			'===== ===== ====='
		)
		time.sleep(10)

	if args.is_noti_to_slack:
		global alert
		alert = Alert('alert')

	db = DB('db', config)
	db.open()
	langs = db.fetch_languages()

	es = ES('es', config.es_host)
	if not es.is_connected:
		print('[CRITICAL][{}.main] Can\'t connect to ElasticSearch.'.format(app_name))
		return

	corpus = Corpus('corpus', args.project_id, db, es, langs)
	for input_file in args.input_files:
		df = get_df(args.path, input_file)
		if args.group_col_name:
			insert_df_with_group_and_tag(df, args.is_preview, args.lang_col_names, args.group_col_name, args.tag_col_name, corpus)
		else:
			if len(args.lang_col_names) == 2:
				insert_df(df, args.is_preview, args.lang_col_names, args.text_col_names, args.tag_col_name, langs, corpus)
			elif len(args.lang_col_names) == 1:
				insert_mono_df(df, args.is_preview, args.lang_col_names[0], args.text_col_names[0], args.tag_col_name, langs, corpus)

		message = '[{}.main] All insertions are complete for {}!'.format(app_name, input_file)
		notify('info', message, args.is_noti_to_slack)

	db.close()


if __name__ == '__main__':
	main()
