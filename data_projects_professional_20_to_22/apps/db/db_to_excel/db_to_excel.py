#!../../../bin/python3

from datetime import datetime
import sys

from cmd_args_db import CMDArgsDB
from config import Config
from libs.corpus.all_parallel_corpus import AllParallelCorpus
from libs.corpus.corpus import Corpus
from libs.corpus.parallel_corpus import ParallelCorpus
from libs.utils.alert import Alert
from libs.utils.code_books import FileFormat
from libs.utils.db import DB
from libs.utils.request_format import RequestFormat


app_name = 'db_to_excel'


def fetch_codes(db):
	langs = db.fetch_languages()
	tags = db.fetch_tags()
	companies = db.fetch_companies()

	return langs, tags, companies


def get_lang_values(langs, lang_codes, min_corpus_ids):
	if min_corpus_ids:
		lang_values = list(zip([langs[lang_code] for lang_code in lang_codes], lang_codes, min_corpus_ids))
		lang_values.sort()
		lang_ids, lang_codes, min_corpus_ids = zip(*lang_values)
	else:
		lang_values = list(zip([langs[lang_code] for lang_code in lang_codes], lang_codes))
		lang_values.sort()
		lang_ids, lang_codes = zip(*lang_values)

	return lang_ids, lang_codes, min_corpus_ids


def get_request_format(args):
	req = RequestFormat('request_format')
	req.path = args.path
	req.output_file = args.output_file
	req.output_file_format = args.output_file_format
	req.max_rows_in_file = args.max_rows_in_file
	req.lang_format = args.lang_format
	req.lang_codes = args.lang_codes
	req.count = args.count
	req.min_chars_count = args.min_chars_count
	req.min_words_count = args.min_words_count
	req.is_tagged_only = args.is_tagged_only
	req.is_not_tagged_only = args.is_not_tagged_only

	return req


def notify(level, message, is_noti_to_slack):
	level = level.upper()
	print('%s [%s]%s' % (str(datetime.now()), level, message))
	if is_noti_to_slack:
		alert.send(level, f'`[{level}]` {message}')


def main():
	args_db = CMDArgsDB('args', [])
	args = args_db.values

	config = Config('config', is_dev=not args.is_production)
	if not config.is_loaded:
		print(f'[CRITICAL][{app_name}.main] Can\'t open config.ini.')
		return

	if args.is_noti_to_slack:
		global alert
		alert = Alert('alert')

	db = DB('db', config)
	db.open()

	langs, tags, companies = fetch_codes(db)
	tag_id = tags.get(args.tag, 0)
	include_company_id = companies.get(args.include_company, 0)
	if args.exclude_companies:
		exclude_company_ids = [companies.get(company, 0) for company in args.exclude_companies]
	else:
		exclude_company_ids = []
 
	if args.is_from_corpus_raw:
		message = f'[{app_name}.main] Extraction all from corpus_raw started!'
		notify('info', message, args.is_noti_to_slack)

		args.output_file, args.output_file_format = 'corpus_raw.xlsx', FileFormat('xlsx')
		req = get_request_format(args)
		corpus = Corpus('corpus', 0, db)
		corpus.fetch(req, is_ignore_not_in_group=args.is_ignore_not_in_group)

		message = f'[{app_name}.main] Extraction all from corpus_raw completed!'
		notify('info', message, args.is_noti_to_slack)
	elif args.lang_codes[0] == 'all':
		message = f'[{app_name}.main] Extraction ALL started!'
		notify('info', message, args.is_noti_to_slack)

		lang_ids = list(langs.values())
		lang_ids.sort()

		args.output_file, args.output_file_format = 'all_pairs', 'xlsx'
		all_parallel_corpus = AllParallelCorpus('all_parallel_corpus', db.conn)
		all_parallel_corpus.fetch(lang_ids, args.count, args.path, args.output_file, args.output_file_format, 1, 100000, 1)

		message = f'[{app_name}.main] Extraction ALL completed!'
		notify('info', message, args.is_noti_to_slack)
	else:
		message = '[{}.main] Extraction {} started!'.format(app_name, ', '.join(args.lang_codes))
		notify('info', message, args.is_noti_to_slack)

		lang_ids, args.lang_codes, args.min_corpus_ids = get_lang_values(langs, args.lang_codes, args.min_corpus_ids)
		exclude_lang_id = langs.get(args.exclude_lang_code, 0)

		if not args.output_file:
			args.output_file = '_'.join(args.lang_codes) + ('_%d' % args.count)
			args.output_file_format = FileFormat('xlsx')

		req = get_request_format(args)
		req.lang_ids = lang_ids
		req.tag_id = tag_id
		req.include_company_id = include_company_id
		req.exclude_company_ids = exclude_company_ids

		parallel_corpus = ParallelCorpus('parallel_corpus', db, req.max_rows_in_file, args.is_noti_to_slack)
		parallel_corpus.fetch(
			req,
			args.min_corpus_ids,
			exclude_lang_id,
			args.check_col_name,
			args.is_cleaning,
			args.is_newest,
			args.is_add_ids,
			args.is_add_delivery,
			args.is_add_tag)

		message = '[{}.main] Extraction {} completed!'.format(app_name, ', '.join(args.lang_codes))
		notify('info', message, args.is_noti_to_slack)

	db.close()


if __name__ == '__main__':
	main()
