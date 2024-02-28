#!../../../bin/python3

from datetime import datetime

from cmd_args_broken_integrities import CMDArgsBrokenIntegrities
from config import Config
from libs.corpus.parallel_corpus import ParallelCorpus
from libs.utils.alert import Alert
from libs.utils.db import DB
from libs.utils.request_format import RequestFormat


app_name = 'broken_integrities'


def get_request_format(args):
	req = RequestFormat('request_format')
	req.path = args.path
	req.output_file = args.output_file
	req.output_file_format = args.output_file_format

	return req


def notify(level, message, is_noti_to_slack):
	level = level.upper()
	print('%s [%s]%s' % (str(datetime.now()), level, message))
	if is_noti_to_slack:
		alert.send(level, f'`[{level}]` {message}')


def main():
	args_broken_integrities = CMDArgsBrokenIntegrities('args_broken_integrities', [])
	args = args_broken_integrities.values

	config = Config('config', is_dev=not args.is_production)
	if not config.is_loaded:
		print(f'[CRITICAL][{app_name}.main] Can\'t open config.ini.')
		return

	if args.is_noti_to_slack:
		global alert
		alert = Alert('alert')

	db = DB('db', config)
	db.open()

	if args.is_dup_lang_in_group:
		req = get_request_format(args)

		parallel_corpus = ParallelCorpus('parallel_corpus', db, req.max_rows_in_file, args.is_noti_to_slack)
		parallel_corpus.fetch_dup_lang_in_group(req)

		message = f'[{app_name}.main] Extraction \'dup_lang_in_group\' completed!'
		notify('info', message, args.is_noti_to_slack)

	db.close()


if __name__ == '__main__':
	main()
