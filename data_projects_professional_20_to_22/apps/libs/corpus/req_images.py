import pandas as pd
import sys
from datetime import datetime

from libs.utils.alert import Alert


class ReqImages:
	__tbl_request = 'req_tr'
	__tbl_response = 'req_tr_res'


	def fetch_req_images_cnt(self, src_lang_id = 0, dst_lang_id = 0):
		sql = " \
			SELECT (SELECT lang_code FROM language WHERE lang_id = Q.src_lang_id) AS src_lang_code, \
				(SELECT lang_code FROM language WHERE lang_id = Q.dst_lang_id) AS dst_lang_code, \
				COUNT(*) AS cnt \
			FROM " + self.__tbl_request + " Q, " + self.__tbl_response + " A \
			WHERE Q.req_id = A.req_id \
				AND Q.content_type = 'I' \
				AND A.selected = 'Y' \
		"
		if src_lang_id > 0:
			sql += " AND Q.src_lang_id = %d" % src_lang_id
		if dst_lang_id > 0:
			sql += " AND Q.dst_lang_id = %d" % dst_lang_id
		sql += " \
			GROUP BY src_lang_code, dst_lang_code \
			ORDER BY src_lang_code, dst_lang_code \
		"
		print('sql: %s' % sql)

		try:
			df = pd.read_sql(sql, self.__conn)
		except:
			self.__alert.send('critical', '`[CRITICAL]` [req_images_stat.fetch_req_images_cnt] %s' % str(sys.exc_info()).replace('"', ' '))
			sys.exit()

		return df


	def fetch_req_images(self, src_lang_id = 0, dst_lang_id = 0):
		sql = " \
			SELECT Q.req_id, \
				(SELECT lang_code FROM language WHERE lang_id = Q.src_lang_id) AS src_lang_code, \
				(SELECT lang_code FROM language WHERE lang_id = Q.dst_lang_id) AS dst_lang_code, \
				REPLACE(Q.content_url, 'http://flittosg.s3.amazonaws.com', 'http://i.fltcdn.net') AS content_url, \
				A.tr_content \
			FROM " + self.__tbl_request + " Q, " + self.__tbl_response + " A \
			WHERE Q.req_id = A.req_id \
				AND Q.content_type = 'I' \
				AND A.selected = 'Y' \
		"
		if src_lang_id > 0:
			sql += " AND Q.src_lang_id = %d" % src_lang_id
		if dst_lang_id > 0:
			sql += " AND Q.dst_lang_id = %d" % dst_lang_id
		sql += " ORDER BY Q.req_id DESC"
		print('sql: %s' % sql)

		try:
			df = pd.read_sql(sql, self.__conn)
		except:
			self.__alert.send('critical', '`[CRITICAL]` [req_images_stat.fetch_req_images] %s' % str(sys.exc_info()).replace('"', ' '))
			sys.exit()

		return df


	def __init__(self, name, conn):
		self.__name = name
		self.__conn = conn
		self.__alert = Alert('alert')
