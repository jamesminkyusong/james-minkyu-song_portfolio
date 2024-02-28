from datetime import datetime
import sys

import pandas as pd

from libs.utils.alert import Alert
from libs.utils.df_utils import DFUtils
from libs.utils.save import Save


class Corpus:
	__alert = Alert('alert')
	__df_utils = DFUtils('df_utils')
	__save = Save('save', max_rows_in_file=500_000)
	__tbl_corpus = 'corpus'
	__tbl_corpus_tags_map = 'corpus_tags_map'
	__tbl_group_tags_map = 'group_tags_map'
	__tbl_dup_corpus = 'duplicated_corpus'
	__tbl_parallel_corpus = 'parallel_corpus'
	__tbl_proj_corpus_map = 'project_corpus_map'


	def insert_mono(self, lang_id1, text1):
		group_id1, corpus_id1 = self.__find_corpus_on_es(lang_id1, text1)

		group_id = 0
		if group_id1 == 0:
			new_group_id = self.__insert_2(0, corpus_id1, lang_id1, text1)
			group_id = new_group_id
		elif group_id1 > 0:
			if self.__proj_id > 0:
				self.__ins_to_proj_corpus_map(self.__proj_id, lang_id1, corpus_id1)
			group_id = group_id1

		return group_id


	def insert(self, lang_id1, text1, lang_id2, text2):
		group_id1, corpus_id1 = self.__find_corpus_on_es(lang_id1, text1)
		group_id2, corpus_id2 = self.__find_corpus_on_es(lang_id2, text2)

		group_id = 0
		if group_id1 == 0 and group_id2 == 0:
			new_group_id = self.__insert_2(0, corpus_id1, lang_id1, text1)
			self.__insert_2(new_group_id, corpus_id2, lang_id2, text2)
			group_id = new_group_id
		elif group_id1 == 0 and group_id2 > 0:
			self.__insert_2(group_id2, corpus_id1, lang_id1, text1)
			if self.__proj_id > 0:
				self.__ins_to_proj_corpus_map(self.__proj_id, lang_id2, corpus_id2)
			group_id = group_id2
		elif group_id1 > 0 and group_id2 == 0:
			if self.__proj_id > 0:
				self.__ins_to_proj_corpus_map(self.__proj_id, lang_id1, corpus_id1)
			self.__insert_2(group_id1, corpus_id2, lang_id2, text2)
			group_id = group_id1
		else:
			if self.__proj_id > 0:
				self.__ins_to_proj_corpus_map(self.__proj_id, lang_id1, corpus_id1)
				self.__ins_to_proj_corpus_map(self.__proj_id, lang_id2, corpus_id2)
			group_id = group_id1

		return group_id


	def insert_with_group_id(self, group_id, lang_id, text):
		group_id2, corpus_id2 = self.__find_corpus_on_es(lang_id, text)
		print(f'group_id2, corpus_id2: {group_id2}, {corpus_id2}')

		if group_id2 > 0:
			if self.__proj_id > 0 and group_id == group_id2:
				self.__ins_to_proj_corpus_map(self.__proj_id, lang_id, corpus_id2)
		else:
			if corpus_id2 > 0:
				if self.__proj_id > 0:
					self.__ins_to_proj_corpus_map(self.__proj_id, lang_id, corpus_id2)
			else:
				self.__insert_2(group_id, corpus_id2, lang_id, text)


	def fetch(self, req, is_ignore_not_in_group=False):
		file_index = 1
		sid = 1
		max_corpus_id = 0

		while True:
			print(f'%s [INFO][corpus.fetch] Extracting corpus_raw ...' % str(datetime.now()))
			df = self.__fetch_step(max_corpus_id, req.max_rows_in_file, is_ignore_not_in_group)
			if len(df) <= 0:
				break

			file_index, sid = self.__save_as_file(req.path, req.output_file, df, file_index, sid)
			max_corpus_id = df.iloc[len(df)-1, 1]


	def __fetch_step(self, max_corpus_id, max_rows_in_file, is_ignore_not_in_group):
		if is_ignore_not_in_group:
			sql = ' \
				SELECT B.id AS corpus_id, (SELECT code FROM languages WHERE id = lang_id) AS lang_code, B.text \
				FROM (SELECT A.id, A.lang_id, (SELECT COUNT(*) FROM parallel_corpus WHERE corpus_id = A.id) AS count_in_group, A.text \
						FROM (SELECT id, lang_id, text \
								FROM corpus \
			'
			if max_corpus_id > 0:
				sql += '		WHERE id < %d' % max_corpus_id
			sql += ' \
								ORDER BY id DESC \
								LIMIT %d) A \
				) B \
				WHERE B.count_in_group > 0 \
			' % max_rows_in_file
		else:
			sql = ' \
				SELECT id AS corpus_id, (SELECT code FROM languages WHERE id = lang_id) AS lang_code, text \
				FROM corpus \
			'
			if max_corpus_id > 0:
				sql += ' WHERE id < %d' % max_corpus_id
			sql += ' \
				ORDER BY id DESC \
				LIMIT %d \
			' % max_rows_in_file

		try:
			df = pd.read_sql(sql, self.__db.conn)
		except:
			message = '[corpus.fetch_step] %s' % str(sys.exc_info()).replace('"', ' ')
			print(message)
			self.__alert.send('critical', message)
			sys.exit()

		return df


	def __save_as_file(self, path, output_file, df, file_index, sid):
		output_file_with_i = ('_%d.' % file_index).join(output_file.rsplit('.', 1))

		self.__df_utils.add_sid(df, sid)
		self.__save.as_file(df, path, output_file_with_i)

		file_index += 1
		sid += len(df)

		return file_index, sid


	def delete(self, lang_id1, lang_id2):
		rows = self.__sel_corpus_by_proj(self.__proj_id, lang_id1, lang_id2)
		for row in rows:
			lang_code = row[0]
			corpus_id = row[1]
			self.__es.delete_by_corpus_id(lang_code, corpus_id)
			self.__del_parallel_corpus(corpus_id)
			self.__del_corpus(corpus_id)


	def __insert_2(self, group_id, corpus_id, lang_id, text):
		if corpus_id <= 0:
			corpus_id = self.__ins_to_corpus(lang_id, text)
			self.__ins_to_corpus_on_es(lang_id, corpus_id, text)
			if self.__proj_id > 0:
				self.__ins_to_proj_corpus_map(self.__proj_id, lang_id, corpus_id)

		new_group_id = self.__ins_to_parallel_corpus(group_id, lang_id, corpus_id)
		if group_id > 0 and new_group_id <= 0:
			current_corpus_id = self.__sel_current_corpus(group_id, lang_id)
			self.__ins_dup_corpus(group_id, lang_id, current_corpus_id, corpus_id)
			self.__up_as_new_corpus(group_id, lang_id, corpus_id)

		return new_group_id


	def __find_corpus_on_es(self, lang_id, text):
		lang_code = next(key for key, value in self.__langs.items() if value == lang_id)
		group_id = 0
		corpus_id, _ = self.__es.find(lang_code, text)

		if corpus_id > 0:
			query = ' \
				SELECT group_id \
				FROM ' + self.__tbl_parallel_corpus + ' \
				WHERE corpus_id = %s \
					AND lang_id = %s \
				ORDER BY group_id DESC \
			'
			values = (corpus_id, lang_id)
			row = self.__db.fetch_row(query, values)

			if row is not None:
				group_id = row[0]

		return group_id, corpus_id


	def __ins_to_corpus(self, lang_id, text):
		query = ' \
			INSERT INTO ' + self.__tbl_corpus + ' (lang_id, text) \
			VALUES (%s, %s) \
			RETURNING id \
		'
		values = (lang_id, text)
		row = self.__db.fetch_row(query, values)

		return row[0] if len(row) > 0 else 0


	def __ins_to_corpus_on_es(self, lang_id, corpus_id, text):
		lang_code = next(key for key, value in self.__langs.items() if value == lang_id)
		self.__es.insert(lang_code, corpus_id, text)


	def __ins_to_parallel_corpus(self, group_id, lang_id, corpus_id):
		query = 'INSERT INTO ' + self.__tbl_parallel_corpus + ' (group_id, lang_id, corpus_id)'
		values = ()
		if group_id > 0:
			query += ' \
				SELECT %s, %s, %s \
				WHERE NOT EXISTS ( \
					SELECT 1 \
					FROM ' + self.__tbl_parallel_corpus + ' \
					WHERE group_id = %s \
						AND lang_id = %s) \
			'
			values = (group_id, lang_id, corpus_id, \
				group_id, lang_id)
		else:
			query += ' \
				SELECT COALESCE(MAX(group_id) + 1, 1), %s, %s \
				FROM ' + self.__tbl_parallel_corpus
			values = (lang_id, corpus_id)
		query += ' RETURNING group_id'
		row = self.__db.execute(query, values)

		return row[0] if len(row) > 0 else 0


	def __ins_to_proj_corpus_map(self, proj_id, lang_id, corpus_id):
		query = ' \
			INSERT INTO ' + self.__tbl_proj_corpus_map + ' (project_id, lang_id, corpus_id) \
			SELECT %s, %s, %s \
			WHERE NOT EXISTS ( \
				SELECT id \
				FROM ' + self.__tbl_proj_corpus_map + ' \
				WHERE project_id = %s \
					AND lang_id = %s \
					AND corpus_id = %s) \
			RETURNING id \
		'
		values = (proj_id, lang_id, corpus_id, \
			proj_id, lang_id, corpus_id)
		self.__db.execute(query, values)


	def __sel_current_corpus(self, group_id, lang_id):
		query = ' \
			SELECT corpus_id \
			FROM ' + self.__tbl_parallel_corpus + ' \
			WHERE group_id = %s \
				AND lang_id = %s \
		'
		values = (group_id, lang_id)
		row = self.__db.fetch_row(query, values)

		return row[0] if row is not None else 0


	def __ins_dup_corpus(self, group_id, lang_id, corpus_id1, corpus_id2):
		query = ' \
			INSERT INTO ' + self.__tbl_dup_corpus + ' (group_id, lang_id, corpus_id1, corpus_id2) \
			SELECT %s, %s, %s, %s \
			WHERE NOT EXISTS ( \
				SELECT id \
				FROM ' + self.__tbl_dup_corpus + ' \
				WHERE group_id = %s \
					AND lang_id = %s \
					AND corpus_id1 = %s \
					AND corpus_id2 = %s) \
			RETURNING id \
		'
		values = (group_id, lang_id, corpus_id1, corpus_id2, \
			group_id, lang_id, corpus_id1, corpus_id2)
		self.__db.execute(query, values)


	def __up_as_new_corpus(self, group_id, lang_id, corpus_id):
		query = ' \
			UPDATE ' + self.__tbl_parallel_corpus + ' \
			SET corpus_id = %s \
			WHERE group_id = %s \
				AND lang_id = %s \
			RETURNING id \
		'
		values = (corpus_id, group_id, lang_id)
		self.__db.execute(query, values)


	def __sel_corpus_by_proj(self, proj_id, lang_id1, lang_id2):
		query = ' \
			SELECT corpus_id \
			FROM project_corpus_map \
			WHERE project_id <> %s \
				AND (lang_id = %s OR lang_id = %s) \
			GROUP BY corpus_id \
			HAVING COUNT(corpus_id) = 0 \
			ORDER BY corpus_id \
		'
		values = (proj_id, lang_id1, lang_id2)
		rows = self.__db.fetch_all(query, values)

		return rows


	def __del_corpus(self, corpus_id):
		query = ' \
			DELETE FROM ' + self.__tbl_corpus + ' \
			WHERE corpus_id = %s \
			CASCADE \
		'
		values = (corpus_id)
		self.__db.execute(query, values)


	def __del_parallel_corpus(self, corpus_id):
		query = ' \
			DELETE FROM ' + self.__tbl_parallel_corpus + ' \
			WHERE group_id IN ( \
				SELECT group_id \
				FROM ' + self.__tbl_parallel_corpus + ' \
				WHERE group_id = (SELECT group_id \
					FROM ' + self.__tbl_parallel_corpus + ' \
					WHERE corpus_id = %s) \
				GROUP BY group_id \
				HAVING COUNT(group_id) = 2 \
			) \
		'
		values = (corpus_id)
		self.__db.execute(query, values)


	def delete_tag(self, group_id):
		query = ' \
			DELETE FROM ' + self.__tbl_group_tags_map + ' \
			WHERE group_id = %s \
			RETURNING id \
		'
		values = (group_id, )
		self.__db.execute(query, values)


	def insert_tag(self, group_id, tag_id, priority, tag_score):
		query = ' \
			INSERT INTO ' + self.__tbl_group_tags_map + ' (group_id, tag_id, priority, score) \
			VALUES (%s, %s, %s, %s) \
			RETURNING id \
		'
		values = (group_id, tag_id, priority, tag_score)
		self.__db.execute(query, values)


	def insert_old_tag(self, group_id, tag_id):
		query = ' \
			INSERT INTO ' + self.__tbl_corpus_tags_map + ' (group_id, tag_id, priority) \
			VALUES (%s, %s, 1) \
			ON CONFLICT (group_id, priority) DO UPDATE SET tag_id = EXCLUDED.tag_id \
			RETURNING id \
		'
		values = (group_id, tag_id)
		self.__db.execute(query, values)


	def update_text(self, corpus_id, text):
		query = ' \
			UPDATE ' + self.__tbl_corpus + ' \
			SET text = %s \
			WHERE id = %s \
			RETURNING id \
		'
		values = (text, corpus_id)
		self.__db.execute(query, values)


	def __init__(self, name, proj_id=0, db=None, es=None, langs=[]):
		self.__name = name
		self.__proj_id = proj_id
		self.__db = db
		self.__es = es
		self.__langs = langs
