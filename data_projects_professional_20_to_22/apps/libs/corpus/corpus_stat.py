import pandas as pd


class CorpusStat:
	__tbl_corpus = 'corpus'
	__tbl_cnt_mono_corpus = 'cnt_mono_corpus'
	__tbl_cnt_2pairs_corpus = 'cnt_2pairs_corpus'
	__tbl_cnt_3pairs_corpus = 'cnt_3pairs_corpus'


	def fetch(self, lang_ids):
		lang_ids_count = len(lang_ids)
		if not 1 <= lang_ids_count <= 3:
			return 0

		if lang_ids_count == 2:
			table_name = self.__tbl_cnt_2pairs_corpus
		elif lang_ids_count == 3:
			table_name = self.__tbl_cnt_3pairs_corpus
		else:
			table_name = self.__tbl_cnt_mono_corpus

		query = (
			'SELECT SUM(cnt)'
			' FROM %s'
			' WHERE %s'
		) % (
			table_name,
			' AND '.join(['lang_id%d = %d' % (index + 1, lang_id) for index, lang_id in enumerate(lang_ids)])
		)
		row = self.__db.fetch_row(query, None)

		return row[0] if row else 0


	def fetch_mono_all_df(self):
		query = ' \
			SELECT (SELECT name FROM languages WHERE id = lang_id1) AS lang_name, \
				(CASE WHEN tag_id = 0 THEN 100 ELSE tag_id END) AS tag_id, \
				COALESCE((SELECT name FROM tags WHERE id = tag_id), \'Unknown\') AS tag_name, \
				cnt \
			FROM ' + self.__tbl_cnt_mono_corpus + ' \
			ORDER BY lang_name, tag_id \
		'
		df = pd.read_sql(query, self.__db.conn)
		df.drop(columns='tag_id', inplace=True)

		return df


	def fetch_2pairs_all_df(self):
		query = ' \
			SELECT (SELECT name FROM languages WHERE id = lang_id1) AS lang_name1, \
				(SELECT name FROM languages WHERE id = lang_id2) AS lang_name2, \
				(CASE WHEN tag_id = 0 THEN 100 ELSE tag_id END) AS tag_id, \
				COALESCE((SELECT name FROM tags WHERE id = tag_id), \'Unknown\') AS tag_name, \
				cnt \
			FROM ' + self.__tbl_cnt_2pairs_corpus + ' \
			ORDER BY lang_name1, lang_name2, tag_id \
		'
		df = pd.read_sql(query, self.__db.conn)
		df.drop(columns='tag_id', inplace=True)

		return df


	def __get_table_name_by(self, lang_ids_count):
		if lang_ids_count == 2:
			table_name = self.__tbl_cnt_2pairs_corpus
		elif lang_ids_count == 3:
			table_name = self.__tbl_cnt_3pairs_corpus
		else:
			table_name = self.__tbl_cnt_mono_corpus

		return table_name


	def clear(self, x_pairs):
		table_name = self.__get_table_name_by(x_pairs)
		query = (
			'UPDATE %s '
			'SET cnt = 0'
		) % (table_name)
		self.__db.execute_without_return(query, None)


	def update(self, lang_ids, count_per_tag):
		lang_ids_count = len(lang_ids)
		if not 1 <= lang_ids_count <= 3:
			return

		table_name = self.__get_table_name_by(lang_ids_count)
		conflict_columns = ['lang_id%d' % (index+1) for index in range(lang_ids_count)] + ['tag_id']
		columns = conflict_columns + ['cnt']
		for key, value in count_per_tag.items():
			query = ' \
				INSERT INTO %s (%s) \
				VALUES (%s) \
				ON CONFLICT (%s) DO UPDATE SET cnt = EXCLUDED.cnt \
				RETURNING id \
			' % (table_name, ', '.join(columns), \
				', '.join([str(x) for x in lang_ids + [key, value]]), \
				', '.join(conflict_columns))
			self.__db.execute(query, None)


	def __init__(self, name, db):
		self.__name = name
		self.__db = db
