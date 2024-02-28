import pandas as pd
import sys
from datetime import datetime

from libs.utils.alert import Alert


class QRPImages:
	__tbl_qr_item = 'qr_item'
	__tbl_qr_tr = 'qr_tr'


	def fetch_qrp_source_images_cnt(self, lang_id):
		sql = " \
			SELECT COUNT(lang_id) AS cnt \
			FROM " + self.__tbl_qr_item + " \
			WHERE lang_id = %d \
		" % lang_id
		print('sql: %s' % sql)

		try:
			df = pd.read_sql(sql, self.__conn)
			cnt = df.loc[0][0]
		except:
			self.__alert.send('critical', '`[CRITICAL]` [qrp_images.qrp_source_images_cnt] %s' % str(sys.exc_info()).replace('"', ' '))
			sys.exit()

		return cnt


	def fetch_qrp_tr_cnt_per_langs(self, lang_id):
		sql = " \
			SELECT (SELECT lang_code FROM language WHERE lang_id = A.orig_lang_id) AS orig_lang_code, \
				(SELECT lang_code FROM language WHERE lang_id = A.tr_lang_id) AS tr_lang_code, \
				COUNT(*) AS cnt \
			FROM (SELECT I.item_id, I.lang_id AS orig_lang_id, T.lang_id AS tr_lang_id \
					FROM " + self.__tbl_qr_item + " I, " + self.__tbl_qr_tr + " T \
					WHERE I.lang_id = %d \
						AND I.item_id = T.item_id \
						AND I.lang_id <> T.lang_id \
					GROUP BY I.item_id, orig_lang_id, tr_lang_id \
					ORDER BY I.item_id) A \
			GROUP BY A.orig_lang_id, A.tr_lang_id \
			ORDER BY tr_lang_code \
		" % lang_id
		print('sql: %s' % sql)

		try:
			df = pd.read_sql(sql, self.__conn)
		except:
			self.__alert.send('critical', '`[CRITICAL]` [qrp_images.fetch_qrp_tr_cnt_per_langs] %s' % str(sys.exc_info()).replace('"', ' '))
			sys.exit()

		return df


	def fetch_qrp_items(self, lang_id):
		sql = " \
			SELECT I.item_id, T.qr_tr_id, T.like_cnt, \
				REPLACE((SELECT lang_code FROM language WHERE lang_id = I.lang_id), 'zh-CN', 'zh') AS orig_lang_code, \
				REPLACE((SELECT lang_code FROM language WHERE lang_id = T.lang_id), 'zh-CN', 'zh') AS tr_lang_code, \
				image_url, \
				(SELECT tr_content FROM qr_tr WHERE item_id = I.item_id AND lang_id = I.lang_id AND status = 'Y' ORDER BY like_cnt DESC, qr_tr_id DESC limit 1) AS orig, \
				T.tr_content AS tr\
			FROM " + self.__tbl_qr_item + " I, " + self.__tbl_qr_tr + " T \
			WHERE I.lang_id = %d \
				AND I.item_id = T.item_id \
				AND I.lang_id <> T.lang_id \
			ORDER BY I.item_id, T.lang_id, T.like_cnt DESC, T.qr_tr_id DESC \
		" % lang_id
		print('sql: %s' % sql)

		try:
			df = pd.read_sql(sql, self.__conn)
			df.drop_duplicates(subset = ['item_id', 'orig_lang_code', 'tr_lang_code'], keep = 'first', inplace = True)
		except:
			self.__alert.send('critical', '`[CRITICAL]` [qrp_images.fetch_qrp_items] %s' % str(sys.exc_info()).replace('"', ' '))
			sys.exit()

		return df


	def __init__(self, name, conn):
		self.__name = name
		self.__conn = conn
		self.__alert = Alert('alert')
