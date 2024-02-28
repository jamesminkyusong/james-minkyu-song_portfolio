#!../../bin/python3

import getopt
import sys
from datetime import datetime
from enum import Enum, auto

from config import Config
from libs.corpus.qrp_images import QRPImages
from libs.corpus.req_images import ReqImages
from libs.utils.alert import Alert
from libs.utils.db import DB
from libs.utils.df_utils import DFUtils


class StatType(Enum):
	QRP_SOURCE_IMAGES_CNT = auto()
	QRP_TR_CNT_PER_LANGS = auto()
	QRP_ITEMS = auto()
	REQ_IMAGES_CNT = auto()


def get_arguments(argv):
	path = ''
	output_file = ''
	max_rows_in_file = 100000
	lang_code = ''
	stat_type = ''
	is_noti_to_slack = False

	opts, _ = getopt.getopt(argv, 'l:m:o:p:s:t:')
	for opt, arg in opts:
		if opt == '-l':
			lang_code = arg
		elif opt == '-m':
			max_rows_in_file = max(int(arg), 1)
		elif opt == '-o':
			output_file = arg
		elif opt == '-p':
			path = arg
		elif opt == '-s':
			is_noti_to_slack = arg.lower() == 'y'
		elif opt == '-t':
			stat_type = arg.lower()

	return path, output_file, max_rows_in_file, lang_code, stat_type, is_noti_to_slack


def fetch_qrp_source_images_cnt(qrp_images, lang_id, lang_code, is_noti_to_slack):
	cnt = qrp_images.fetch_qrp_source_images_cnt(lang_id)
	message = '[show_images_stat.fetch_qrp_source_images_cnt] The count of %s images : %d' % (lang_code, cnt)
	notify('info', message, is_noti_to_slack)


def fetch_qrp_tr_cnt_per_langs(qrp_images, lang_id, lang_code, is_noti_to_slack):
	df = qrp_images.fetch_qrp_tr_cnt_per_langs(lang_id)
	cnt_per_orig_lang = [row[1] + ' : ' + str(row[2]) for row in df.values]
	message = '[show_images_stat.fetch_qrp_tr_cnt_per_langs] The count of %s is ...\n%s' % (lang_code, '\n'.join(cnt_per_orig_lang))
	notify('info', message, is_noti_to_slack)


def fetch_qrp_items(qrp_images, lang_id, lang_code, path, output_file, max_rows_in_file, is_noti_to_slack):
	df = qrp_images.fetch_qrp_items(lang_id)
	df_utils = DFUtils('df_utils')
	df_utils.add_sid(df)
	df_utils.save(df, path, output_file, max_rows_in_file)
	message = '[show_images_stat.fetch_qrp_items] Original texts and translations for %s images are saved! / %s ' % (lang_code, output_file)
	notify('info', message, is_noti_to_slack)


def fetch_req_images_cnt(req_images, is_noti_to_slack):
	df = req_images.fetch_req_images_cnt()
	req_images_cnt = [row[0] + ' -> ' + row[1] + ' : %d' % int(row[2]) for row in df.values]
	message = '[show_images_stat.fetch_req_images_cnt] The count of request images ...\n%s' % '\n'.join(req_images_cnt)
	notify('info', message, is_noti_to_slack)


def notify(level, message, is_noti_to_slack):
	level = level.upper()
	print('%s [%s]%s' % (str(datetime.now()), level, message))
	if is_noti_to_slack:
		alert.send(level, f'`[{level}]` {message}')


def show_usage(error_code, supported_stat):
	supported_stat_str = '|'.join(supported_stat)

	if error_code == 1:
		print('[ERROR] STAT_TYPE should be in %s !' % supported_stat_str)
	elif error_code == 2:
		print('[ERROR] LANG is not supported!')
	elif error_code == 3:
		print('[ERROR] PATH, OUTPUT_FILE is needed for %s!' % StatType.QRP_ITEMS.name)
	else:
		print('Usage (required) :')
		print('    ./show_images_stat.sh -l LANG -t %s' % supported_stat_str)
		print('Usage (optional) :')
		print('    ./show_images_stat.sh -l LANG -t %s -s SLACK_YN(def: N)' % supported_stat_str)
		print()
		print('#1 QR Place 한국어 이미지 개수')
		print('    ./show_images_stat.sh -l ko -t %s' % StatType.QRP_SOURCE_IMAGES_CNT.name)
		print('#2 QR Place 한국어 이미지의 언어별 번역 개수')
		print('    ./show_images_stat.sh -l ko -t %s' % StatType.QRP_TR_CNT_PER_LANGS.name)
		print('#3 QR Place 한국어 이미지별 원문 및 번역')
		print('    ./show_images_stat.sh -p PATH -o OUTPUT_FILE -l ko -t %s' % StatType.QRP_ITEMS.name)
		print('#4 언어별 이미지 요청 개수')
		print('    ./show_images_stat.sh -t %s' % StatType.REQ_IMAGES_CNT.name)


def main():
	langs = {
		'ar': 3,
		'zh': 11,
		'en': 17,
		'fr': 20,
		'de': 22,
		'hi': 25,
		'id': 27,
		'ja': 30,
		'ko': 33,
		'ms': 38,
		'pt': 45,
		'ru': 48,
		'es': 52,
		'tr': 57,
		'th': 56,
		'vi': 61,
		'tl': 62
	}
	supported_stat = [stat_type.name.lower() for stat_type in StatType]

	config = Config("config")
	if not config.is_loaded:
		print("[CRITICAL][show_images_stat.main] Can't open config.ini.")
		return

	# FOR TEST
	config.db_host = '100.20.218.55'

	path, output_file, max_rows_in_file, lang_code, stat_type, is_noti_to_slack = get_arguments(sys.argv[1:])
	if len(stat_type) <= 0:
		show_usage(0, supported_stat)
		return

	if is_noti_to_slack:
		global alert
		alert = Alert('slack')

	if not stat_type in supported_stat:
		show_usage(1, supported_stat)
		return

	if stat_type == StatType.QRP_ITEMS.name.lower() \
		and (len(path) <= 0 or len(output_file) <= 0):
		show_usage(3, supported_stat)
		return

	db = DB('db', config)
	db.open()

	qrp_images = QRPImages('qrp_images', db.conn)
	req_images = ReqImages('req_images', db.conn)

	if stat_type == StatType.QRP_SOURCE_IMAGES_CNT.name.lower():
		lang_id = langs[lang_code]
		fetch_qrp_source_images_cnt(qrp_images, lang_id, lang_code, is_noti_to_slack)
	elif stat_type == StatType.QRP_TR_CNT_PER_LANGS.name.lower():
		lang_id = langs[lang_code]
		fetch_qrp_tr_cnt_per_langs(qrp_images, lang_id, lang_code, is_noti_to_slack)
	elif stat_type == StatType.QRP_ITEMS.name.lower():
		lang_id = langs[lang_code]
		fetch_qrp_items(qrp_images, lang_id, lang_code, path, output_file, max_rows_in_file, is_noti_to_slack)
	elif stat_type == StatType.REQ_IMAGES_CNT.name.lower():
		fetch_req_images_cnt(req_images, is_noti_to_slack)

	db.close()


if __name__ == '__main__':
	main()
