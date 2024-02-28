#!../../../bin/python3

from datetime import datetime
import pandas as pd
import time

from cmd_args_excel2db import CMDArgsExcel2DB
from config import Config
from libs.corpus.corpus import Corpus
from libs.utils.alert import Alert
from libs.utils.db import DB
from libs.utils.es import ES
from libs.utils.reader import Reader


app_name = 'excel2db'

now_f = lambda: str(datetime.now()).split('.')[0]
min_score = 0.5


def get_df(input_file_p):
	print('{} [INFO][{}.get_df] Reading {} ...'.format(now_f(), app_name, input_file_p))

	reader = Reader('reader')
	df = reader.get_simple_df(input_file_p)

	print('{} [INFO][{}.get_df] {:,} rows fetched'.format(now_f(), app_name, len(df)))
	return df


def get_tag_ids_and_scores(df, tag_name_col_ns, tag_score_col_ns, tag_map):
	all_tag_ids = []
	all_tag_scores = []

	if tag_name_col_ns and tag_score_col_ns:
		for tag_names, tag_scores in zip(df[tag_name_col_ns].values, df[tag_score_col_ns].values):
			passed_tag_ids = []
			passed_tag_scores = []
			for index, (tag_name, tag_score) in enumerate(zip(tag_names, tag_scores)):
				if (not pd.isnull(tag_name)) and ((index == 0) or (tag_score >= min_score)):
					passed_tag_ids += [tag_map[tag_name]]
					passed_tag_scores += [int(tag_score * 100) / 100]
			all_tag_ids += [passed_tag_ids]
			all_tag_scores += [passed_tag_scores]

	return all_tag_ids, all_tag_scores


def preview_corpus(df, lang_map, group_id_col_ns, lang_col_ns, text_col_ns, all_tag_ids=None, all_tag_scores=None):
	all_count = len(df)

	if not lang_col_ns:
		for index, group_id in enumerate(df[group_id_col_ns].values):
			h_index = index + 1
			print('[{:,}/{:,}] group_id : {}'.format(h_index, all_count, group_id))
			if all(map(lambda x: x is not None, [all_tag_ids, all_tag_scores])):
				print('[{:,}/{:,}] tags     : {}, {}'.format(h_index, all_count, all_tag_ids[index], all_tag_scores[index]))
	elif len(lang_col_ns) == 2:
		for index, (lang, lang2, text, text2) in enumerate(df[[*lang_col_ns, *text_col_ns]].values):
			h_index = index + 1
			lang_id = lang_map[lang]
			lang_id2 = lang_map[lang2]
			print('[{:,}/{:,}] {}/{} : {}'.format(h_index, all_count, lang, lang_id, text))
			print('[{:,}/{:,}] {}/{} : {}'.format(h_index, all_count, lang2, lang_id2, text2))
			if all([all_tag_ids, all_tag_scores]):
				print('[{:,}/{:,}] tags  : {}, {}'.format(h_index, all_count, all_tag_ids[index], all_tag_scores[index]))
	elif len(lang_col_ns) == 1:
		for index, (lang, text) in enumerate(df[[lang_col_ns[0], text_col_ns[0]]].values):
			h_index = index + 1
			lang_id = lang_map[lang]
			print('[{:,}/{:,}] {}/{} : {}'.format(h_index, all_count, lang, lang_id, text))
			if all([all_tag_ids, all_tag_scores]):
				print('[{:,}/{:,}] tags  : {}, {}'.format(h_index, all_count, all_tag_ids[index], all_tag_scores[index]))


def insert_corpus(corpus, lang_ids, texts, lang_ids2=None, texts2=None):
	all_count = len(lang_ids)
	group_ids = []

	if lang_ids2 is not None and texts2 is not None:
		for index, (lang_id, text, lang_id2, text2) in enumerate(zip(lang_ids, texts, lang_ids2, texts2)):
			group_id = corpus.insert(lang_id, text, lang_id2, text2)
			group_ids += [group_id]

			h_index = index + 1
			if h_index % 1_000 == 0 or h_index == all_count:
				print('{} [INFO][{}.insert_corpus] {:,}/{:,} rows inserted'.format(now_f(), app_name, h_index, all_count))
	else:
		for index, (lang_id, text) in enumerate(zip(lang_ids, texts)):
			group_id = corpus.insert_mono(lang_id, text)
			group_ids += [group_id]

			h_index = index + 1
			if h_index % 1_000 == 0 or h_index == all_count:
				print('{} [INFO][{}.insert_corpus] {:,}/{:,} rows inserted'.format(now_f(), app_name, h_index, all_count))

	return group_ids


def insert_tags(df, group_ids, all_tag_ids, all_tag_scores, corpus):
	all_count = len(group_ids)
	for index, (group_id, tag_ids, tag_scores) in enumerate(zip(group_ids, all_tag_ids, all_tag_scores)):
		if group_id <= 0:
			continue

		corpus.delete_tag(group_id)
		for tag_index, (tag_id, tag_score) in enumerate(zip(tag_ids, tag_scores)):
			corpus.insert_tag(group_id, tag_id, tag_index + 1, tag_score)

		h_index = index + 1
		if h_index % 1_000 == 0 or h_index == all_count:
			print('{} [INFO][{}.insert_tag] {:,}/{:,} rows inserted'.format(now_f(), app_name, h_index, all_count))


def insert_mono_corpus(df, lang_col_n, text_col_n, all_tag_ids, all_tag_scores, lang_map, corpus):
	langs = df[lang_col_n]
	texts = df[text_col_n]
	lang_ids = list(map(lambda x: lang_map[x], langs))

	group_ids = insert_corpus(
		corpus,
		lang_ids, texts
	)

	if all([all_tag_ids, all_tag_scores]):
		insert_tags(
			df,
			group_ids,
			all_tag_ids, all_tag_scores,
			corpus
		)


def insert_parallel_corpus(df, lang_col_ns, text_col_ns, all_tag_ids, all_tag_scores, lang_map, corpus):
	langs, langs2 = df[lang_col_ns[0]], df[lang_col_ns[1]]
	texts, texts2 = df[text_col_ns[0]], df[text_col_ns[1]]
	lang_ids, lang_ids2 = list(map(lambda x: lang_map[x], langs)), list(map(lambda x: lang_map[x], langs2))

	group_ids = insert_corpus(
		corpus,
		lang_ids, texts,
		lang_ids2=lang_ids2, texts2=texts2
	)

	if all([all_tag_ids, all_tag_scores]):
		insert_tags(
			df,
			group_ids,
			all_tag_ids, all_tag_scores,
			corpus
		)


def notify(level, message, is_noti_to_slack):
	level = level.upper()
	print('%s [%s]%s' % (now_f(), level, message))
	if is_noti_to_slack:
		alert.send(level, '`[%s]` %s' % (level, message))


def main():
	args_excel2db = CMDArgsExcel2DB('cmd_args_excel2db', ['path', 'input_files'])
	args = args_excel2db.values

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
	lang_map = db.fetch_languages()
	tag_map = db.fetch_tags()

	es = ES('es', config.es_host)
	if not es.is_connected:
		print('[CRITICAL][{}.main] Can\'t connect to ElasticSearch.'.format(app_name))
		return

	corpus = Corpus('corpus', args.project_id, db, es, lang_map)
	for input_file_p in args.input_files_p:
		df = get_df(input_file_p)
		all_tag_ids, all_tag_scores = get_tag_ids_and_scores(df, args.tag_name_col_ns, args.tag_score_col_ns, tag_map)

		lang_col_ns = args.lang_col_ns
		if args.langs:
			for index, lang in enumerate(args.langs):
				df.insert(len(df.columns), f'lang_{index+1}', [lang] * len(df))
			lang_col_ns = df.columns[-2:]

		if args.is_preview:
			preview_corpus(
				df,
				lang_map,
				args.group_id_col_n, lang_col_ns, args.text_col_ns,
				all_tag_ids=all_tag_ids, all_tag_scores=all_tag_scores
			)
			continue

		if args.group_id_col_n in df.columns:
			insert_tags(
				df,
				df[args.group_id_col_n],
				all_tag_ids, all_tag_scores,
				corpus
			)
		elif len(lang_col_ns) == 2:
			insert_parallel_corpus(
				df,
				lang_col_ns, args.text_col_ns,
				all_tag_ids, all_tag_scores,
				lang_map,
				corpus
			)
		elif len(lang_col_ns) == 1:
			insert_mono_corpus(
				df,
				args.lang_col_ns[0], args.text_col_ns[0],
				all_tag_ids, all_tag_scores,
				lang_map,
				corpus
			)

		message = '[{}.main] All insertions are complete for {}!'.format(app_name, input_file_p)
		notify('info', message, args.is_noti_to_slack)

	db.close()


if __name__ == '__main__':
	main()
