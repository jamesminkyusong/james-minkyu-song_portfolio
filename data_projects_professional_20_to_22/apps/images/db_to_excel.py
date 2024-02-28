#!../../bin/python3

from datetime import datetime
import sys

from config import Config
from cmd_opts_child import CMDOptsChild
from libs.corpus.req_images import ReqImages
from libs.utils.alert import Alert
from libs.utils.db import DB
from libs.utils.df_utils import DFUtils


def fetch_req_images(path, output_file, max_rows_in_file, lang_codes, src_lang_id, dst_lang_id, conn):
	req_images = ReqImages('req_images', conn)
	df = req_images.fetch_req_images(src_lang_id, dst_lang_id)

	if len(df) > 0:
		df_utils = DFUtils('df_utils')
		df_utils.add_sid(df)
		df_utils.save(df, path, output_file, max_rows_in_file)
		message = '[db_to_excel.fetch_req_images] %d requested images from %s to %s are saved in %s!' % (len(df), lang_codes[0], lang_codes[1], output_file)
	else:
		message = '[db_to_excel.fetch_req_images] No requested images from %s to %s!' % (lang_codes[0], lang_codes[1])

	return True, message


def notify(level, message, is_noti_to_slack):
	level = level.upper()
	print('%s [%s]%s' % (str(datetime.now()), level, message))
	if is_noti_to_slack:
		alert.send(level, f'`[{level}]` {message}')


def main():
	opts = CMDOptsChild('opts', sys.argv[1:])
	if not opts.is_loaded:
		return

	langs = { \
		'ar': 3, \
		'cs': 14, \
		'de': 22, \
		'en': 17, \
		'es': 52, \
		'fi': 19, \
		'fr': 20, \
		'hi': 25, \
		'id': 27, \
		'it': 29, \
		'ja': 30, \
		'ko': 33, \
		'ms': 38, \
		'nl': 16, \
		'pl': 44, \
		'pt': 45, \
		'ru': 48, \
		'th': 56, \
		'tl': 62, \
		'tr': 57, \
		'vi': 61, \
		'sw': 63, \
		'sv': 53, \
		'zh': 11, \
		'zhtw': 12 \
	}

	config = Config('config')
	if not config.is_loaded:
		print("[CRITICAL][db_to_excel.main] Can't open config.ini.")
		sys.exit()

	if opts.is_noti_to_slack:
		global alert
		alert = Alert('alert')

	# FOR TEST
	config.db_host = '44.232.134.107'

	db = DB('db', config)
	db.open()

	result, message = fetch_req_images(opts.path, opts.output_file, opts.max_rows_in_file, opts.lang_codes, langs[opts.lang_codes[0]], langs[opts.lang_codes[1]], db.conn)
	if result:
		notify('info', message, opts.is_noti_to_slack)

	db.close()


if __name__ == '__main__':
	main()
