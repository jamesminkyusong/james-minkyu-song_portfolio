import math
import pandas as pd
import string
import sys
from datetime import datetime

from libs.utils.alert import Alert


class AllParallelCorpus:
	__rows_in_excel = 1000
	__tbl_parallel_corpus = 'parallel_corpus'


	def __fetch_max_group_id(self):
		sql = 'SELECT MAX(group_id) \
			FROM ' + self.__tbl_parallel_corpus
		print('sql: %s' % sql)

		try:
			df = pd.read_sql(sql, self.__conn)
			max_group_id = df.loc[0][0]
		except:
			self.__alert.send('critical', '`[CRITICAL]` [all_parallel_corpus.fetch_max_group_id] %s' % str(sys.exc_info()).replace('"', ' '))
			sys.exit()

		return max_group_id


	def __save_to_excel(self, all_corpus_df, excel_index, sid, path, filename, ext):
		if excel_index == 1:
			excel_file = '%s.%s' % (filename, ext)
		else:
			excel_file = '%s_%d.%s' % (filename, excel_index, ext)

		if len(all_corpus_df) > self.__rows_in_excel:
			first_corpus_df = all_corpus_df.iloc[0:self.__rows_in_excel, :]
			first_corpus_df.insert(0, 'sid', list(range(sid, sid + self.__rows_in_excel)))
			first_corpus_df.to_excel('%s/%s' % (path, excel_file), index = False, engine = 'xlsxwriter')
			return all_corpus_df.iloc[self.__rows_in_excel:, :]
		else:
			all_corpus_df.insert(0, 'sid', list(range(sid, sid + len(all_corpus_df))))
			all_corpus_df.to_excel('%s/%s' % (path, excel_file), index = False, engine = 'xlsxwriter')
			return None


	def fetch(self, lang_ids, counts, path, filename, ext, start_group_id = 1, end_group_id = 0, excel_index = 1):
		current_group_id = start_group_id
		max_group_id = end_group_id if end_group_id > 0 else self.__fetch_max_group_id()
		sid = (excel_index - 1) * self.__rows_in_excel + 1

		all_corpus_df = pd.DataFrame()
		while current_group_id <= max_group_id:
			print("%s [INFO][all_parallel_corpus.fetch][%d/%d] Extracting..." % (str(datetime.now()), current_group_id, max_group_id - start_group_id + 1))
			corpus_df = self.__fetch_step(lang_ids, current_group_id)
			all_corpus_df = pd.concat([all_corpus_df, corpus_df])
			if len(corpus_df) <= 0:
				self.__save_to_excel(all_corpus_df, excel_index, sid, path, filename, ext)
				self.__alert.send("info", "`[INFO]` [all_parallel_corpus.fetch] Extracted #%d : %s.%s" % (excel_index, filename, ext))
				break
			elif len(all_corpus_df) >= self.__rows_in_excel:
				all_corpus_df = self.__save_to_excel(all_corpus_df, excel_index, sid, path, filename, ext)
				# print("%s [INFO][all_parallel_corpus.fetch][%d/%d] Extracted #%d : %s.%s" % (str(datetime.now()), current_group_id, max_group_id - start_group_id + 1, excel_index, filename, ext))
				self.__alert.send("info", "`[INFO]` [all_parallel_corpus.fetch] Extracted #%d : %s.%s" % (excel_index, filename, ext))

				excel_index += 1
				sid += self.__rows_in_excel

			current_group_id += 1


	def __fetch_step(self, lang_ids, group_id):
		table_aliases = string.ascii_uppercase[:len(lang_ids)]
		codes_and_texts_in_SELECT = []
		tables_in_FROM = []
		lang_ids_in_WHERE = []

		for index in range(len(lang_ids)):
			table_alias = table_aliases[index]

			codes_and_texts_in_SELECT.append('(SELECT code FROM languages WHERE id = %s.lang_id) AS code%d, %s.corpus_id AS corpus_id%d, (SELECT text FROM corpus WHERE id = %s.corpus_id) AS text%d' % (table_alias, index + 1, table_alias, index + 1, table_alias, index + 1))
			tables_in_FROM.append('(SELECT Y.id AS lang_id, corpus_id FROM (SELECT lang_id, corpus_id FROM parallel_corpus WHERE group_id = %d) X RIGHT JOIN languages Y ON X.lang_id = Y.id) %s' % (group_id, table_alias))
			if index < len(lang_ids) - 1:
				next_table_alias = table_aliases[index + 1]
				lang_ids_in_WHERE.append('%s.lang_id < %s.lang_id' % (table_alias, next_table_alias))

		sql = 'SELECT %s \
				FROM %s \
				WHERE %s' \
			% (', '.join(codes_and_texts_in_SELECT), \
				', '.join(tables_in_FROM), \
				' AND '.join(lang_ids_in_WHERE))
		# print('sql: %s' % sql)

		try:
			corpus_df = pd.read_sql(sql, self.__conn)
		except:
			self.__alert.send('critical', '`[CRITICAL]` [all_parallel_corpus.fetch_step] %s' % str(sys.exc_info()).replace('"', ' '))
			sys.exit()

		return corpus_df


	def __init__(self, name, conn):
		self.name = name
		self.__conn = conn
		self.__alert = Alert('alert')
