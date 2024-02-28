import itertools
import math
import pandas as pd
import sys
from datetime import datetime

from libs.utils.alert import Alert


class SpeechesStat:
	__rows_per_step = 10_000
	__tbl_events = 'b2b_events'
	__tbl_event_db = 'b2b_event_db'
	__tbl_event_res = 'b2b_event_res'
	__tbl_event_users = 'b2b_event_users'


	def fetch_event_ids(self):
		sql = " \
			SELECT event_id \
			FROM " + self.__tbl_events + " \
			WHERE event_type = 'R' \
			ORDER BY event_id \
		"
		print('sql: %s' % sql)

		try:
			df = pd.read_sql(sql, self.__conn)
		except:
			self.__alert.send('critical', '`[CRITICAL]` [speeches_stat.fetch_event_ids] %s' % str(sys.exc_info()).replace('"', ' '))
			sys.exit()

		return df


	def fetch_users_cnt(self, useless_events, lang_id):
		uniq_users_cnt_SELECT = 'SELECT COUNT(DISTINCT C.user_id)'
		users_cnt_SELECT = 'SELECT COUNT(C.user_id)'
		useless_events_WHERE = ', '.join([str(event_id) for event_id in useless_events])
		sql = " \
			FROM " + self.__tbl_events + " A, " + self.__tbl_event_db + " B, " + self.__tbl_event_res + " C \
			WHERE A.event_id IN (SELECT event_id \
					FROM " + self.__tbl_events + " \
					WHERE src_lang_id = %d \
						AND event_type = 'R' \
						AND event_id NOT IN (%s)) \
				AND A.event_id = B.event_id \
				AND B.origin_id = C.origin_id \
				AND C.selected = 'Y' \
		" % (lang_id, useless_events_WHERE)

		try:
			df = pd.read_sql(uniq_users_cnt_SELECT + sql, self.__conn)
			uniq_users_cnt = df.loc[0][0]

			df = pd.read_sql(users_cnt_SELECT + sql, self.__conn)
			users_cnt = df.loc[0][0]
		except:
			self.__alert.send('critical', '`[CRITICAL]` [speeches_stat.fetch_users_cnt] %s' % str(sys.exc_info()).replace('"', ' '))
			sys.exit()

		return uniq_users_cnt, users_cnt


	def fetch_speeches_count(self, event_id):
		sql = " \
			SELECT COUNT(*) \
			FROM " + self.__tbl_events + " A, " + self.__tbl_event_db + " B, " + self.__tbl_event_res + " C \
			WHERE A.event_id = %d \
				AND A.event_id = B.event_id \
				AND B.origin_id = C.origin_id \
				AND C.selected = 'Y' \
		" % event_id
		print('sql: %s' % sql)

		try:
			df = pd.read_sql(sql, self.__conn)
		except:
			self.__alert.send('critical', '`[CRITICAL]` [speeches_stat.fetch_speeches_count] %s' % str(sys.exc_info()).replace('"', ' '))
			sys.exit()

		return df


	def fetch_length(self, event_id):
		sql = " \
			SELECT SUM(C.duration) \
			FROM " + self.__tbl_events + " A, " + self.__tbl_event_db + " B, " + self.__tbl_event_res + " C \
			WHERE A.event_id = %d \
				AND A.event_id = B.event_id \
				AND B.origin_id = C.origin_id \
				AND C.selected = 'Y' \
		" % event_id
		print('sql: %s' % sql)

		try:
			df = pd.read_sql(sql, self.__conn)
		except:
			self.__alert.send('critical', '`[CRITICAL]` [speeches_stat.fetch_length] %s' % str(sys.exc_info()).replace('"', ' '))
			sys.exit()

		return df


	def fetch_uniq_users_cnt_per_country(self, useless_events, lang_id, count=0):
		useless_events_WHERE = ', '.join([str(event_id) for event_id in useless_events])
		sql = " \
			SELECT (SELECT country FROM country WHERE country_id = (SELECT country_id FROM users WHERE user_id = D.user_id)) AS country, COUNT(*) AS cnt \
			FROM (SELECT DISTINCT(user_id) \
					FROM b2b_events A, b2b_event_db B, b2b_event_res C \
					WHERE A.event_id IN (SELECT event_id \
							FROM b2b_events \
							WHERE src_lang_id = %d \
								AND event_type = 'R' \
								AND event_id NOT IN (%s)) \
						AND A.event_id = B.event_id \
						AND B.origin_id = C.origin_id \
						AND C.selected = 'Y') D \
			GROUP BY country \
			ORDER BY cnt DESC \
		" % (lang_id, useless_events_WHERE)
		if count > 0:
			sql += 'LIMIT %d' % count
		print('sql: %s' % sql)

		try:
			df = pd.read_sql(sql, self.__conn)
		except:
			self.__alert.send('critical', '`[CRITICAL]` [speeches_stat.fetch_speeches_count] %s' % str(sys.exc_info()).replace('"', ' '))
			sys.exit()

		return df


	def fetch_users_cnt_per_country(self, useless_events, lang_id, count=0):
		useless_events_WHERE = ', '.join([str(event_id) for event_id in useless_events])
		sql = " \
			SELECT (SELECT country FROM country WHERE country_id = (SELECT country_id FROM users WHERE user_id = C.user_id)) AS country, COUNT(*) AS cnt \
			FROM b2b_events A, b2b_event_db B, b2b_event_res C \
			WHERE A.event_id IN (SELECT event_id \
					FROM b2b_events \
					WHERE src_lang_id = %d \
						AND event_type = 'R' \
						AND event_id NOT IN (%s)) \
				AND A.event_id = B.event_id \
				AND B.origin_id = C.origin_id \
				AND C.selected = 'Y' \
			GROUP BY country \
			ORDER BY cnt DESC \
		" % (lang_id, useless_events_WHERE)
		if count > 0:
			sql += 'LIMIT %d' % count
		print('sql: %s' % sql)

		try:
			df = pd.read_sql(sql, self.__conn)
		except:
			self.__alert.send('critical', '`[CRITICAL]` [speeches_stat.fetch_users_cnt_per_country] %s' % str(sys.exc_info()).replace('"', ' '))
			sys.exit()

		return df


	def fetch_users_cnt_per_device(self, useless_events, lang_id):
		useless_events_WHERE = ', '.join([str(event_id) for event_id in useless_events])
		sql = " \
			SELECT (SELECT COALESCE(os, 'unk') FROM users WHERE user_id = C.user_id) AS os, COUNT(*) AS cnt \
			FROM b2b_events A, b2b_event_db B, b2b_event_res C \
			WHERE A.event_id IN (SELECT event_id \
					FROM b2b_events \
					WHERE src_lang_id = %d \
						AND event_type = 'R' \
						AND event_id NOT IN (%s)) \
				AND A.event_id = B.event_id \
				AND B.origin_id = C.origin_id \
				AND C.selected = 'Y' \
			GROUP BY os \
			ORDER BY cnt DESC \
		" % (lang_id, useless_events_WHERE)
		print('sql: %s' % sql)

		try:
			df = pd.read_sql(sql, self.__conn)
		except:
			self.__alert.send('critical', '`[CRITICAL]` [speeches_stat.fetch_users_cnt_per_device] %s' % str(sys.exc_info()).replace('"', ' '))
			sys.exit()

		return df


	def fetch_per_gender_and_age(self, useless_events, lang_code):
		lang_code = 'zh-CN' if lang_code == 'zh' else lang_code

		stat = {}
		matrix = [['M', 'F', 'U'], [10, 20, 30, 40, 50]]
		for key in [x for x in itertools.product(*matrix)]:
			stat[key] = (0, 0)

		min_origin_id = self.__fetch_min_origin_id(useless_events, lang_code)
		max_origin_id = self.__fetch_max_origin_id(useless_events, lang_code)
		print('%s [INFO][speeches_stat.fetch_per_gender_and_age] min/max origin id: %d / %d' % (str(datetime.now()), min_origin_id, max_origin_id))

		step = 1
		steps = math.ceil((max_origin_id - min_origin_id + 1) / self.__rows_per_step)

		while min_origin_id <= max_origin_id:
			print('%s [INFO][speeches_stat.fetch_per_gender_and_age][%d / %d] Extracting : %s' % (str(datetime.now()), step, steps, lang_code))
			df = self.__fetch_step(useless_events, lang_code, min_origin_id, self.__rows_per_step)
			if len(df) <= 0:
				break

			max_origin_id_in_step = 0
			for index, row in df.iterrows():
				gender = row[0]
				age_group = int(row[1])
				counts = row[2]
				secs = row[3]
				max_origin_id_in_step = max(int(row[4]), max_origin_id_in_step)
				stat[(gender, age_group)] = tuple(map(sum, zip(stat[(gender, age_group)], (counts, secs))))

			step += 1
			min_origin_id = max_origin_id_in_step + 1

		return stat


	def __fetch_min_origin_id(self, useless_events, lang_code):
		useless_events_WHERE = ', '.join([str(event_id) for event_id in useless_events])
		sql = " \
			SELECT MIN(origin_id) \
			FROM " + self.__tbl_event_db + " \
			WHERE event_id = (SELECT MIN(event_id) \
				FROM " + self.__tbl_events + " \
				WHERE src_lang_id = (SELECT lang_id \
						FROM language \
						WHERE lang_code = '" + lang_code + "') \
					AND event_type = 'R' \
					AND event_id NOT IN (" + useless_events_WHERE + ")) \
		"
		print('sql: %s' % sql)

		return self.__fetch_origin_id(sql)


	def __fetch_max_origin_id(self, useless_events, lang_code):
		useless_events_WHERE = ', '.join([str(event_id) for event_id in useless_events])
		sql = " \
			SELECT MAX(origin_id) \
			FROM " + self.__tbl_event_db + " \
			WHERE event_id = (SELECT MAX(event_id) \
				FROM " + self.__tbl_events + " \
				WHERE src_lang_id = (SELECT lang_id \
						FROM language \
						WHERE lang_code = '" + lang_code + "') \
					AND event_type = 'R' \
					AND event_id NOT IN (" + useless_events_WHERE + ")) \
		"
		print('sql: %s' % sql)

		return self.__fetch_origin_id(sql)


	def __fetch_origin_id(self, sql):
		try:
			df = pd.read_sql(sql, self.__conn)
			origin_id = df.loc[0][0]
		except:
			self.__alert.send('critical', '`[CRITICAL]` [speeches_stat.fetch_origin_id] %s' % str(sys.exc_info()).replace('"', ' '))
			sys.exit()

		return origin_id


	def __fetch_step(self, useless_events, lang_code, min_origin_id, limit):
		useless_events_WHERE = ', '.join([str(event_id) for event_id in useless_events])
		sql = " \
			SELECT D.gender, \
				D.age_group, \
				COUNT(*) AS count, \
				SUM(D.duration) AS secs, \
				MAX(D.origin_id) \
			FROM (SELECT (SELECT (CASE WHEN gender IN ('M', 'F') THEN gender ELSE 'U' END) AS gender \
						FROM " + self.__tbl_event_users + " \
						WHERE user_id = C.user_id \
						ORDER BY join_date DESC \
						LIMIT 1), \
					(SELECT (CASE WHEN age_group IN ('10', '20', '30', '40', '50') THEN age_group ELSE '20' END) AS age_group \
						FROM " + self.__tbl_event_users + " \
						WHERE user_id = C.user_id \
						ORDER BY join_date DESC \
						LIMIT 1), \
					(CASE WHEN C.duration IS NULL THEN 0 ELSE C.duration END) AS duration, \
					B.origin_id \
				FROM " + self.__tbl_events + " A, " + self.__tbl_event_db + " B, " + self.__tbl_event_res + " C \
				WHERE A.event_id IN (SELECT event_id \
						FROM " + self.__tbl_events + " \
						WHERE src_lang_id = (SELECT lang_id \
								FROM language \
								WHERE lang_code = '" + lang_code + "') \
							AND event_type = 'R' \
							AND event_id NOT IN (" + useless_events_WHERE + ")) \
					AND A.event_id = B.event_id \
					AND B.origin_id = C.origin_id \
					AND C.selected = 'Y' \
					AND B.origin_id >= %d \
					ORDER BY A.event_id, B.origin_id \
					LIMIT %d) D \
			GROUP BY gender, age_group \
			ORDER BY gender, age_group \
		" % (min_origin_id, limit)
		print('sql: %s' % sql)

		try:
			df = pd.read_sql(sql, self.__conn)
		except:
			self.__alert.send('critical', '`[CRITICAL]` [speeches_stat.fetch_step] %s' % str(sys.exc_info()).replace('"', ' '))
			sys.exit()

		return df


	def __init__(self, name, conn):
		self.__name = name
		self.__conn = conn
		self.__alert = Alert('alert')
