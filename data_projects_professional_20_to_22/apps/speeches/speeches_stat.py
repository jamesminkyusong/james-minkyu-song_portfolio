#!../../bin/python3

"""
Purpose
-------
URL : https://docs.google.com/spreadsheets/d/1XLpxP2eeIhJQ-Ii71nzx5ukQltsvS1XOlK1MeEz4a3I

Parameters
----------
--lang_code* : language code
--stat_type* : users_cnt | cnt_len_per_event | users_cnt_per_country | user_cnt_per_device | cnt_len_per_gender_age

Example
-------
#1 영어 발화자 수 (음성 시트)
	./speeches_stat.py --lang_code en --stat_type users_cnt

#2 한국어 음성 개수 및 분량 (음성 시트)
	./speeches_stat.py --lang_code ko --stat_type cnt_len_per_event

#3 중국어 국가별 발화자 수 (음성 (국가별) 시트)
	./speeches_stat.py --lang_code zh --stat_type users_cnt_per_country

#4 프랑스어 기기별 발화자 수 (음성 (기기별) 시트)
	./speeches_stat.py --lang_code fr --stat_type users_cnt_per_device

#5 일본어 성별/연령별 개수 및 분량 (음성 (성별/연령대별) 시트)
	./speeches_stat.py --lang_code ja --stat_type cnt_len_per_gender_age
"""


from datetime import datetime

from cmd_args_stat import CMDArgsStat
from config import Config
from libs.corpus.speeches_stat import SpeechesStat
from libs.utils.alert import Alert
from libs.utils.db import DB


def get_useless_events():
	useless_events = []

	with open('./useless_events.txt') as f:
		useless_events = [int(x) for x in f.readlines()]
		f.close()

	return useless_events


def fetch_users_cnt(speeches_stat, useless_events, lang_id, lang_code, is_noti_to_slack):
	print(f'[INFO][speeches_stat.fetch_users_cnt] Calculating {lang_code} users ...')
	uniq_users_cnt, users_cnt = speeches_stat.fetch_users_cnt(useless_events, lang_id)
	message = f'[speeches_stat.fetch_users_cnt] {lang_code} uniq_users: {uniq_users_cnt} / users: {users_cnt}'
	notify('info', message, is_noti_to_slack)


def fetch_users_cnt_per_country(speeches_stat, useless_events, lang_id, lang_code, is_noti_to_slack):
	print(f'[speeches_stat.fetch_users_cnt_per_country] Calculating {lang_code} users per country ...')
	keys = ['uniq users', 'users']
	uniq_users_cnt_df = speeches_stat.fetch_uniq_users_cnt_per_country(useless_events, lang_id)
	users_cnt_df = speeches_stat.fetch_users_cnt_per_country(useless_events, lang_id)

	for key, df in zip(keys, [uniq_users_cnt_df, users_cnt_df]):
		cnt_per_country = [row[0] + ' : ' + str(row[1]) for row in df.values]
		total_cnt = sum([int(row[1]) for row in df.values])
		message = '[speeches_stat.fetch_users_cnt_per_country] The count of %s %s : %d\n%s' % (lang_code, key, total_cnt, ', '.join(cnt_per_country))
		notify('info', message, is_noti_to_slack)


def fetch_users_cnt_per_device(speeches_stat, useless_events, lang_id, lang_code, is_noti_to_slack):
	print(f'[speeches_stat.fetch_users_cnt_per_device] Calculating {lang_code} users per device ...')
	users_cnt_df = speeches_stat.fetch_users_cnt_per_device(useless_events, lang_id)

	cnt_per_device = [row[0] + ' : ' + str(row[1]) for row in users_cnt_df.values]
	total_cnt = sum([int(row[1]) for row in users_cnt_df.values])
	message = '[speeches_stat.fetch_users_cnt_per_device] The count of %s : %d\n%s' % (lang_code, total_cnt, ', '.join(cnt_per_device))
	notify('info', message, is_noti_to_slack)


def fetch_cnt_and_len_per_event(speeches_stat, useless_events, is_noti_to_slack):
	print(f'[speeches_stat.fetch_cnt_and_len_per_event] Calculating count and length per event ...')
	event_ids_df = speeches_stat.fetch_event_ids()
	for row in event_ids_df.values:
		event_id = row[1]
		if event_id in useless_events:
			continue

		speeches_count_df = speeches_stat.fetch_speeches_count(event_id)
		speeches_length_df = speeches_stat.fetch_length(event_id)

		message = '[speeches_stat.fetch_cnt_and_len_per_event] Stat : %s / %s' % (str(speeches_count_df.iloc[0, 0]), str(speeches_length_df.iloc[0, 0]))
		notify('info', message, is_noti_to_slack)


def fetch_cnt_and_len_per_gender_and_age(speeches_stat, useless_events, lang_code, is_noti_to_slack):
	print(f'[speeches_stat.fetch_cnt_and_len_per_gender_and_age] Calculating {lang_code} count and length per gender and age ...')
	speeches_stat_dict = speeches_stat.fetch_per_gender_and_age(useless_events, lang_code)
	message = '[speeches_stat.fetch_cnt_and_len_per_gender_and_age] %s : %s' % (lang_code, str(speeches_stat_dict))
	notify('info', message, is_noti_to_slack)


def notify(level, message, is_noti_to_slack):
	level = level.upper()
	print('%s [%s]%s' % (str(datetime.now()), level, message))
	if is_noti_to_slack:
		alert.send(level, f'`[{level}]` {message}')


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
	stat_types = ['users_cnt', 'cnt_len_per_event', 'users_cnt_per_country', 'users_cnt_per_device', 'cnt_len_per_gender_age']

	args_stat = CMDArgsStat('cmd_args_stat', sorted(langs.keys()), stat_types, ['lang_code', 'stat_type'])
	args = args_stat.values

	config = Config('config')

	if args.is_noti_to_slack:
		global alert
		alert = Alert('alert')

	# FOR TEST
	config.db_host = '44.238.195.167'

	db = DB('db', config)
	db.open()

	useless_events = get_useless_events()

	speeches_stat = SpeechesStat('speeches_stat', db.conn)
	if args.stat_type == 'users_cnt':
		fetch_users_cnt(speeches_stat, useless_events, langs[args.lang_code], args.lang_code, args.is_noti_to_slack)
	elif args.stat_type == 'cnt_len_per_event':
		fetch_cnt_and_len_per_event(speeches_stat, useless_events, args.is_noti_to_slack)
	elif args.stat_type == 'users_cnt_per_country':
		fetch_users_cnt_per_country(speeches_stat, useless_events, langs[args.lang_code], args.lang_code, args.is_noti_to_slack)
	elif args.stat_type == 'users_cnt_per_device':
		fetch_users_cnt_per_device(speeches_stat, useless_events, langs[args.lang_code], args.lang_code, args.is_noti_to_slack)
	elif args.stat_type == 'cnt_len_per_gender_age':
		fetch_cnt_and_len_per_gender_and_age(speeches_stat, useless_events, args.lang_code, args.is_noti_to_slack)

	db.close()


if __name__ == '__main__':
	main()
