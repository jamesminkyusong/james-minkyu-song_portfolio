#!../../bin/python3

from datetime import datetime
import sys

from cmd_args_db import CMDArgsDB
from config import Config
from libs.corpus.speeches_corpus import SpeechesCorpus
from libs.utils.alert import Alert
from libs.utils.db import DB


def notify(level, message, is_noti_to_slack):
	level = level.upper()
	print('%s [%s]%s' % (str(datetime.now()), level, message))
	if is_noti_to_slack:
		alert.send(level, f'`[{level}]` {message}')


def main():
	args_db = CMDArgsDB('cmd_args_db', ['path', 'output_file', 'event_id'])
	args = args_db.values

	config = Config('config')

	# FOR TEST
	config.db_host = '100.20.218.55'

	if args.is_noti_to_slack:
		global alert
		alert = Alert('alert')

	message = f'[db_to_excel.main] Extracting EventID #{args.event_id} ...'
	notify('info', message, args.is_noti_to_slack)

	db = DB('db', config)
	db.open()
	speeches_corpus = SpeechesCorpus('speeches_corpus', db.conn)
	speeches_corpus.fetch_and_save(args.path, args.output_file, args.max_rows_in_file, args.event_id)
	db.close()

	message = f'[db_to_excel.main] Extraction EventID #{args.event_id} completed!'
	notify('info', message, args.is_noti_to_slack)


if __name__ == '__main__':
	main()
