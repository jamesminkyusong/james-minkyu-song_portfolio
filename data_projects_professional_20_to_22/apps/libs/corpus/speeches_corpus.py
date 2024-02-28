import pandas as pd
import sys

from libs.utils.alert import Alert
from libs.utils.df_utils import DFUtils


class SpeechesCorpus:
	# 기존
	__tbl_events = 'b2b_events'
	__tbl_event_db = 'b2b_event_db'
	__tbl_event_res = 'b2b_event_res'
	__tbl_event_users = 'b2b_event_users'

	# 신규
	__tbl_user_meta = 'user_meta'
	__tbl_voice_corpus = 'voice_corpus'


	def fetch_and_save(self, path, output_file, max_rows_in_file, event_id):
		current_origin_id = 0
		sid = 1
		count = 1

		df_utils = DFUtils('df_utils')
		while True:
			speeches_df = self.__fetch_step(max_rows_in_file, event_id, current_origin_id)
			df_utils.add_sid(speeches_df, sid)
			df_utils.save(speeches_df, path, f'_{count}.'.join(output_file.split('.')), max_rows_in_file)

			if len(speeches_df) >= max_rows_in_file:
				sid += len(speeches_df)
				count += 1
				current_origin_id = int(speeches_df.iloc[-1, 1])
			else:
				break


	def __fetch_step(self, max_rows_in_file, event_id, current_origin_id):
		sql = f" \
			SELECT B.origin_id, \
				C.origin_res_id, \
				A.event_id, \
				A.src_lang_id, \
				B.content, \
				C.tr_content_url, \
				C.duration AS secs, \
				(SELECT user_id FROM {self.__tbl_event_users} WHERE user_id = C.user_id ORDER BY join_date DESC LIMIT 1), \
				(SELECT username FROM users WHERE user_id = C.user_id), \
				(SELECT country FROM country WHERE country_id = (SELECT country_id FROM users WHERE user_id = C.user_id)), \
				(SELECT gender FROM {self.__tbl_event_users} WHERE user_id = C.user_id ORDER BY join_date DESC LIMIT 1), \
				(SELECT age_group FROM {self.__tbl_event_users} WHERE user_id = C.user_id ORDER BY join_date DESC LIMIT 1) \
			FROM {self.__tbl_events} A, {self.__tbl_event_db} B, {self.__tbl_event_res} C \
			WHERE A.event_id = {event_id} \
				AND A.event_id = B.event_id \
				AND B.origin_id = C.origin_id \
				AND C.selected = 'Y' \
		"
		if current_origin_id > 0:
			sql += f' AND b.origin_id > {current_origin_id}'
		sql += f'ORDER BY a.event_id, b.origin_id \
			LIMIT {max_rows_in_file}'
		print(f'sql: {sql}')

		try:
			speeches_df = pd.read_sql(sql, self.__conn)
		except:
			self.__alert.send('critical', '[speeches_corpus.fetch_step] %s' % str(sys.exc_info()).replace('"', ' '))
			sys.exit()

		return speeches_df


	def insert_user_meta(self, id, name, gender, age_group):
		query = " \
			INSERT INTO " + self.__tbl_event_users + " (id, name, gender, age_group) \
				SELECT %s, %s, %s, %s \
				WHERE NOT EXISTS ( \
					SELECT id \
					FROM " + self.__tbl_user_meta + " \
					WHERE id = %s \
		"
		values = (id, name, gender, age_group, \
			id)
		self.__db.execute(query, values)


	def insert_voice(self, lang_id, text, voice_url, user_id, partner_id):
		query = " \
			INSERT INTO " + self.__tbl_voice_corpus + " (lang_id, text, voice_url, user_id, partner_id) \
				VALUES (%s, %s, %s, %s, %s) \
		"
		self.__db.execute(query, values)


	def __init__(self, name, conn):
		self.__name = name
		self.__conn = conn
		self.__alert = Alert('alert')
