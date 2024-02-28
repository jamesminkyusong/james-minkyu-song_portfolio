from datetime import datetime
import math
import string
import sys
import pandas as pd

from libs.utils.alert import Alert
from libs.utils.code_books import LanguageFormat
from libs.utils.df_utils import DFUtils
from libs.utils.lang_code_converter import LangCodeConverter
from libs.utils.save import Save


class ParallelCorpus:
	__alert = Alert('alert')
	__df_utils = DFUtils('df_utils')
	__rows_per_step = 100
	__tbl_corpus_tags_map = 'corpus_tags_map'
	__tbl_group_tags_map = 'group_tags_map'
	__tbl_parallel_corpus = 'parallel_corpus'
	__tbl_project_corpus_map = 'project_corpus_map'


	def fetch(self, req, min_corpus_ids, exclude_lang_id, check_col_name, is_cleaning, is_newest, is_add_ids, is_add_delivery, is_add_tag):
		min_group_id = self.__fetch_min_group_id(req.lang_ids)
		max_group_id = self.__fetch_max_group_id(req.lang_ids)

		all_corpus_df = pd.DataFrame()
		file_index = 1
		sid = 1
		step = 1
		steps = math.ceil((max_group_id - min_group_id + 1) / self.__rows_per_step)
		fetched_count = 0

		while min_group_id <= max_group_id:
			print('{} [INFO][parallel_corpus.fetch][step: {:,}/{:,}][fetched: {:,}] Fetching {} ...'.format(str(datetime.now()), step, steps, fetched_count, str(req.lang_codes)))
			corpus_df = self.__fetch_step(
				req,
				min_corpus_ids,
				exclude_lang_id,
				check_col_name,
				max_group_id if is_newest else min_group_id,
				is_newest,
				is_add_ids,
				is_add_delivery,
				is_add_tag)
			all_corpus_df = pd.concat([all_corpus_df, corpus_df])

			fetched_count = (sid - 1) + len(all_corpus_df)
			if fetched_count >= req.count:
				all_corpus_df = all_corpus_df.head(req.count - (sid - 1))
				break

			all_corpus_df, file_index, sid = self.__split_and_save(all_corpus_df, file_index, sid, req, save_remainder=False)

			step += 1
			if is_newest:
				max_group_id -= self.__rows_per_step
			else:
				min_group_id += self.__rows_per_step

		self.__split_and_save(all_corpus_df, file_index, sid, req, save_remainder=True)


	def fetch_dup_lang_in_group(self, req):
		max_group_id = self.__fetch_max_group_id()

		all_corpus_df = pd.DataFrame()
		file_index = 1
		sid = 1
		step = 1
		steps = math.ceil(max_group_id / self.__rows_per_step)
		fetched_count = 0

		while max_group_id > 0:
			print('{} [INFO][parallel_corpus.fetch_dup_lang_in_group][step: {:,}/{:,}][fetched: {:,}] Fetching ...'.format(str(datetime.now()), step, steps, fetched_count))
			corpus_df = self.__fetch_step_dup_lang_in_group(max_group_id, max_group_id-(self.__rows_per_step-1))
			all_corpus_df = pd.concat([all_corpus_df, corpus_df])

			fetched_count = (sid - 1) + len(all_corpus_df)
			all_corpus_df, file_index, sid = self.__split_and_save(all_corpus_df, file_index, sid, req, save_remainder=False)

			step += 1
			max_group_id -= self.__rows_per_step

		self.__split_and_save(all_corpus_df, file_index, sid, req, save_remainder=True)


	def __fetch_min_group_id(self, lang_ids=None):
		if lang_ids is None:
			sql = f' \
				SELECT MIN(group_id) \
				FROM {self.__tbl_parallel_corpus} \
			'
		else:
			SELECT = ['SELECT MIN(group_id) AS group_id FROM %s WHERE lang_id = %d' % (self.__tbl_parallel_corpus, lang_id) for lang_id in lang_ids]
			tables_in_FROM = ' UNION '.join(SELECT)
			sql = f' \
				SELECT MAX(A.group_id) \
				FROM ({tables_in_FROM}) A \
			'

		print('sql: %s' % sql)
		return self.__fetch_group_id(sql)


	def __fetch_max_group_id(self, lang_ids=None):
		if lang_ids is None:
			sql = f' \
				SELECT MAX(group_id) \
				FROM {self.__tbl_parallel_corpus} \
			'
		else:
			SELECT = ['SELECT MAX(group_id) AS group_id FROM %s WHERE lang_id = %d' % (self.__tbl_parallel_corpus, lang_id) for lang_id in lang_ids]
			tables_in_FROM = ' UNION '.join(SELECT)
			sql = f' \
				SELECT MIN(A.group_id) \
				FROM ({tables_in_FROM}) A \
			'

		print('sql: %s' % sql)
		return self.__fetch_group_id(sql)


	def __fetch_group_id(self, sql):
		try:
			df = pd.read_sql(sql, self.__db.conn)
			group_id = df.iloc[0, 0]
		except:
			message = '[parallel_corpus.fetch_group_id] %s' % str(sys.exc_info()).replace('"', ' ')
			print(message)
			self.__alert.send('critical', message)
			sys.exit()

		return group_id


	def __fetch_step(self, req, min_corpus_ids, exclude_lang_id, check_col_name, group_id, is_newest, is_add_ids, is_add_delivery, is_add_tag):
		sql = self.__get_fetch_sql(
			req,
			min_corpus_ids,
			exclude_lang_id,
			group_id,
			is_newest,
			is_add_ids,
			is_add_delivery,
			is_add_tag)

		try:
			df = pd.read_sql(sql, self.__db.conn)
			if any([req.min_chars_count > 1, req.min_words_count > 1]):
				df = self.__filter_by_length(df, req, check_col_name)
			for col_n in filter(lambda col_n: col_n in df.columns, ['score_1', 'score_2', 'score_3']):
				df[col_n].apply(lambda x: '' if x == 0 else x)
		except:
			message = '[parallel_corpus.fetch_step] %s' % str(sys.exc_info()).replace('"', ' ')
			print(message)
			self.__alert.send('critical', message)
			sys.exit()

		return df


	def __fetch_step_dup_lang_in_group(self, max_group_id, min_group_id):
		sql = f' \
			SELECT group_id, (SELECT code FROM languages WHERE id = lang_id) AS lang_code, corpus_id, (SELECT text FROM corpus WHERE id = corpus_id) AS text \
			FROM parallel_corpus \
			WHERE (group_id, lang_id) IN ( \
					SELECT group_id, lang_id \
					FROM parallel_corpus \
					WHERE group_id BETWEEN {min_group_id} AND {max_group_id} \
					GROUP BY group_id, lang_id \
					HAVING COUNT(id) >= 2 \
					ORDER BY group_id) \
			ORDER BY group_id DESC, lang_id, corpus_id DESC \
		'

		try:
			df = pd.read_sql(sql, self.__db.conn)
		except:
			message = '[parallel_corpus.fetch_step] %s' % str(sys.exc_info()).replace('"', ' ')
			print(message)
			self.__alert.send('critical', message)
			sys.exit()

		return df


	def __filter_by_length(self, df, req, check_col_name):
		if req.min_chars_count > 1:
			filter_func = lambda row, lang_index: len(row[lang_index] if isinstance(row[lang_index], str) else '') >= req.min_chars_count
			col_name_suffix = '_chars_cnt'
		else:
			filter_func = lambda row, lang_index: len((row[lang_index] if isinstance(row[lang_index], str) else '').split(' ')) >= req.min_words_count
			col_name_suffix = '_words_cnt'

		col_names = []
		if check_col_name:
			col_names = [[index, value] for index, value in enumerate(list(df.columns)) if value == check_col_name]
		if not col_names:
			col_names = [[index, value] for index, value in enumerate(list(df.columns)) if value in req.lang_codes]
		lang_indices_for_filter = [col[0] for col in col_names]
		col_names_of_cnt = [col[1] + col_name_suffix for col in col_names]

		new_rows = []
		new_cnt_rows = []

		for row in df.values:
			if any([lang_index for lang_index in lang_indices_for_filter if filter_func(row, lang_index)]):
				new_rows.append(row)
				new_cnt_rows.append([len(row[lang_index]) for lang_index in lang_indices_for_filter])

		df = pd.DataFrame(new_rows, columns=list(df.columns))
		df_of_cnt = pd.DataFrame(new_cnt_rows, columns=col_names_of_cnt)
		for col_name in col_names_of_cnt:
			df[col_name] = df_of_cnt[col_name].values

		return df


	def __get_fetch_sql(self, req, min_corpus_ids, exclude_lang_id, group_id, is_newest, is_add_ids, is_add_delivery, is_add_tag):
		table_aliases = string.ascii_uppercase[:len(req.lang_ids)]
		corpus_tags_map_table_alias = 'Z'
		corpus_ids_in_SELECT = []
		texts_in_SELECT = []
		deliveries_in_SELECT = []
		tables_in_FROM = []
		group_ids_ranges_in_WHERE = []
		group_ids_in_WHERE = []
		lang_ids_WHERE = []
		exclude_lang_id_in_WHERE = '{} NOT IN (SELECT lang_id FROM {} WHERE group_id = A.group_id)'.format(exclude_lang_id, self.__tbl_parallel_corpus) if exclude_lang_id > 0 else ''
		include_company_id_in_WHERE = []
		exclude_company_ids_in_WHERE = None

		lang_code_converter = LangCodeConverter('lang_code_converter')
		for index in range(len(req.lang_ids)):
			table_alias = table_aliases[index]
			lang_code_alias = lang_code_converter.iso639_1_to_bcp47(req.lang_codes[index]) if req.lang_format == LanguageFormat.BCP47 else req.lang_codes[index]

			if is_add_ids:
				corpus_ids_in_SELECT.append('%s.corpus_id AS "%s_id"' % (table_alias, lang_code_alias))
			texts_in_SELECT.append('(SELECT text FROM corpus WHERE id = %s.corpus_id) AS "%s"' % (table_alias, lang_code_alias))
			if is_add_delivery:
				deliveries_in_SELECT.append('(SELECT title FROM projects WHERE id = (SELECT project_id FROM %s WHERE corpus_id = %s.corpus_id ORDER BY project_id DESC LIMIT 1)) AS "%s_delivery"' % (self.__tbl_project_corpus_map, table_alias, lang_code_alias))

			tables_in_FROM.append('parallel_corpus %s' % table_alias)

			if is_newest:
				group_ids_range_tuple = (table_alias, group_id - self.__rows_per_step + 1, group_id)
			else:
				group_ids_range_tuple = (table_alias, group_id, group_id + self.__rows_per_step - 1)
			group_ids_ranges_in_WHERE.append('%s.group_id BETWEEN %s AND %s' % group_ids_range_tuple)

			if index < len(req.lang_ids) - 1:
				next_table_alias = table_aliases[index + 1]
				group_ids_in_WHERE.append('%s.group_id = %s.group_id' % (table_alias, next_table_alias))
			lang_ids_WHERE.append('%s.lang_id = %d' % (table_alias, req.lang_ids[index]))

			if req.include_company_id > 0:
				include_company_id_in_WHERE.append(f'{req.include_company_id} IN (SELECT partner_id FROM projects WHERE id IN (SELECT project_id FROM {self.__tbl_project_corpus_map} WHERE corpus_id = {table_alias}.corpus_id))')

		if req.exclude_company_ids is not None and req.exclude_company_ids:
			intersect_projects_sql = ' INTERSECT '.join([f'(SELECT project_id FROM project_corpus_map WHERE corpus_id = {table_alias}.corpus_id)' for table_alias in table_aliases[0:len(req.lang_ids)]])
			intersect_projects_sql += ' INTERSECT (SELECT id FROM projects WHERE partner_id IN (SELECT id FROM partners WHERE id IN ({})))'.format(', '.join([str(company_id) for company_id in req.exclude_company_ids]))
			exclude_company_ids_in_WHERE = f'(SELECT COUNT(*) FROM ({intersect_projects_sql}) Y) = 0'

		if req.is_tagged_only or req.tag_id > 0:
			tables_in_FROM.append('%s %s' % (self.__tbl_corpus_tags_map, corpus_tags_map_table_alias))
			group_ids_in_WHERE.append('%s.group_id = %s.group_id' % (table_aliases[0], corpus_tags_map_table_alias))

		sql = 'SELECT '
		if is_add_ids:
			sql += ' %s.group_id, ' % table_aliases[0]
		sql += ', '.join(
				[x for x in [
					', '.join(corpus_ids_in_SELECT),
					', '.join(texts_in_SELECT),
					', '.join(deliveries_in_SELECT)
					] if x
				]
			)
		if is_add_tag:
			sql += ", COALESCE((SELECT name FROM tags WHERE id = (SELECT tag_id FROM %s WHERE group_id = %s.group_id)), '') AS tag" % (self.__tbl_corpus_tags_map, table_aliases[0])
			sql += ", COALESCE((SELECT name FROM tags WHERE id = (SELECT tag_id FROM %s WHERE group_id = %s.group_id AND priority = 1)), '') AS new_tag_1" % (self.__tbl_group_tags_map, table_aliases[0])
			sql += ", COALESCE((SELECT score FROM %s WHERE group_id = %s.group_id AND priority = 1), 0) AS score_1" % (self.__tbl_group_tags_map, table_aliases[0])
			sql += ", COALESCE((SELECT name FROM tags WHERE id = (SELECT tag_id FROM %s WHERE group_id = %s.group_id AND priority = 2)), '') AS new_tag_2" % (self.__tbl_group_tags_map, table_aliases[0])
			sql += ", COALESCE((SELECT score FROM %s WHERE group_id = %s.group_id AND priority = 2), 0) AS score_2" % (self.__tbl_group_tags_map, table_aliases[0])
			sql += ", COALESCE((SELECT name FROM tags WHERE id = (SELECT tag_id FROM %s WHERE group_id = %s.group_id AND priority = 3)), '') AS new_tag_3" % (self.__tbl_group_tags_map, table_aliases[0])
			sql += ", COALESCE((SELECT score FROM %s WHERE group_id = %s.group_id AND priority = 3), 0) AS score_3" % (self.__tbl_group_tags_map, table_aliases[0])
		sql += ' FROM %s' % ', '.join(tables_in_FROM)
		sql += ' WHERE ' + ' AND '.join(
				[x for x in [
					' AND '.join(group_ids_ranges_in_WHERE),
					' AND '.join(group_ids_in_WHERE),
					' AND '.join(lang_ids_WHERE)
					] if x
				]
			)
		if min_corpus_ids:
			min_corpus_ids_in_WHERE = ' OR '.join(['%s.corpus_id > %d' % (table_aliases[index], min_corpus_id) for index, min_corpus_id in enumerate(min_corpus_ids)])
			if min_corpus_ids_in_WHERE:
				sql += f' AND ({min_corpus_ids_in_WHERE})'
		if exclude_lang_id_in_WHERE:
			sql += ' AND %s' % exclude_lang_id_in_WHERE
		if include_company_id_in_WHERE:
			sql += ' AND ' + ' AND '.join(include_company_id_in_WHERE)
		elif exclude_company_ids_in_WHERE:
			sql += ' AND ' + exclude_company_ids_in_WHERE
		if req.is_tagged_only:
			sql += ' AND %s.tag_id > 0' % corpus_tags_map_table_alias
		elif req.is_not_tagged_only:
			sql += ' AND NOT EXISTS (SELECT id FROM %s WHERE group_id = %s.group_id)' % (self.__tbl_corpus_tags_map, table_aliases[0])
		elif req.tag_id > 0:
			sql += ' AND %s.tag_id = %d' % (corpus_tags_map_table_alias, req.tag_id)
		if is_newest:
			sql += ' ORDER BY A.group_id DESC'

		print('sql: %s' % sql)
		return sql


	def __split_and_save(self, df, file_index, sid, req, save_remainder):
		while df is not None and len(df) > 0 and any([save_remainder, len(df) >= req.max_rows_in_file]):
			saved_rows = min(len(df), req.max_rows_in_file)
			df = self.__save_as_file(req, df, file_index, sid)

			message = '[parallel_corpus.split_and_save] Extracted #{} and saved {:,} rows : {} / {}'.format(file_index, saved_rows, str(req.lang_codes), req.output_file)
			print(message)
			self.__alert.send('info', message)

			file_index += 1
			sid += req.max_rows_in_file

		return df, file_index, sid


	def __save_as_file(self, req, df, file_index, sid):
		if file_index == 1:
			output_file_with_index = req.output_file
		else:
			output_file_with_index = ('_%d.' % file_index).join(req.output_file.split('.'))

		first_df = df.head(min(len(df), req.max_rows_in_file))
		self.__df_utils.add_sid(first_df, sid)
		self.__save.as_file(first_df, req.path, output_file_with_index)

		return df.iloc[req.max_rows_in_file:, :] if len(df) > req.max_rows_in_file else None


	def fetch_count(self, lang_ids, lang_codes, exclude_company_ids):
		min_group_id = self.__fetch_min_group_id(lang_ids)
		max_group_id = self.__fetch_max_group_id(lang_ids)
		if min_group_id is None or max_group_id is None:
			return 0, {}

		count_per_tag = {}
		step = 1
		steps = math.ceil((max_group_id - min_group_id + 1) / self.__rows_per_step)

		while min_group_id <= max_group_id:
			print('{} [INFO][parallel_corpus.fetch_count][step: {:,}/{:,}] Fetching {} ...'.format(str(datetime.now()), step, steps, str(lang_codes)))
			df = self.__fetch_count_step(lang_ids, min_group_id, exclude_company_ids)
			for row in df.values:
				key = str(row[0])
				count_per_tag[key] = count_per_tag.get(key, 0) + row[1]
			step += 1
			min_group_id += self.__rows_per_step

		return sum(count_per_tag.values()), count_per_tag


	def __fetch_count_step(self, lang_ids, min_group_id=1, exclude_company_ids=None):
		table_aliases = string.ascii_uppercase[:len(lang_ids)]
		tables_in_FROM = []
		group_ids_ranges_in_WHERE = []
		group_ids_in_WHERE = []
		lang_ids_in_WHERE = []
		exclude_company_ids_in_WHERE = None

		for index, lang_id in enumerate(lang_ids):
			table_alias = table_aliases[index]

			tables_in_FROM.append(f'parallel_corpus {table_alias}')

			upper_group_id = min_group_id + self.__rows_per_step - 1
			group_ids_ranges_in_WHERE.append(f'{table_alias}.group_id BETWEEN {min_group_id} AND {upper_group_id}')
			if index < len(lang_ids) - 1:
				next_table_alias = table_aliases[index + 1]
				group_ids_in_WHERE.append(f'{table_alias}.group_id = {next_table_alias}.group_id')
			lang_ids_in_WHERE.append(f'{table_alias}.lang_id = {lang_id}')

		if exclude_company_ids is not None:
			intersect_projects_sql = ' INTERSECT '.join([f'(SELECT project_id FROM project_corpus_map WHERE corpus_id = {table_alias}.corpus_id)' for table_alias in table_aliases[0:len(lang_ids)]])
			intersect_projects_sql += ' INTERSECT (SELECT id FROM projects WHERE partner_id IN (SELECT id FROM partners WHERE id IN ({})))'.format(', '.join([str(company_id) for company_id in exclude_company_ids]))
			exclude_company_ids_in_WHERE = f'(SELECT COUNT(*) FROM ({intersect_projects_sql}) Y) = 0'

		SELECT = 'tag_id, COUNT(tag_id)'
		SUB_SELECT = 'COALESCE((SELECT tag_id FROM corpus_tags_map WHERE group_id = A.group_id), 0) AS tag_id'
		SUB_FROM = ', '.join(tables_in_FROM)
		SUB_WHERE = ' AND '.join(
			[x for x in [
				' AND '.join(group_ids_ranges_in_WHERE),
				' AND '.join(group_ids_in_WHERE),
				' AND '.join(lang_ids_in_WHERE),
				exclude_company_ids_in_WHERE
				] if x
			]
		)
		sql = f' \
			SELECT {SELECT} \
			FROM (SELECT {SUB_SELECT} \
					FROM {SUB_FROM} \
					WHERE {SUB_WHERE}) Z \
			GROUP BY tag_id \
		'
		print('sql: %s' % sql)

		try:
			df = pd.read_sql(sql, self.__db.conn)
		except:
			message = '[parallel_corpus.fetch_count_step] %s' % str(sys.exc_info()).replace('"', ' ')
			print(message)
			self.__alert.send('critical', message)
			sys.exit()

		return df


	def delete_duplicated_corpus(self, current_group_id, new_group_id):
		query = ' \
			DELETE FROM parallel_corpus \
			WHERE corpus_id IN ( \
				SELECT corpus_id \
				FROM parallel_corpus \
				WHERE group_id = %s \
					AND lang_id IN ( \
							SELECT lang_id \
							FROM parallel_corpus \
							WHERE group_id = %s \
						) \
			) \
			RETURNING id \
		'
		values = (current_group_id, new_group_id)
		self.__db.execute(query, values)


	def update_group_id(self, new_group_id, current_group_id):
		query = ' \
			UPDATE parallel_corpus \
			SET group_id = %s \
			WHERE corpus_id IN ( \
				SELECT corpus_id \
				FROM parallel_corpus \
				WHERE group_id = %s \
					AND lang_id NOT IN ( \
							SELECT lang_id \
							FROM parallel_corpus \
							WHERE group_id = %s \
						) \
			) \
			RETURNING id \
		'
		values = (new_group_id, current_group_id, new_group_id)
		self.__db.execute(query, values)


	def __init__(self, name, db, max_rows_in_file=500_000, is_noti_to_slack=False):
		self.name = name
		self.__db = db
		self.__save = Save('save', max_rows_in_file=max_rows_in_file)
		self.__is_noti_to_slack = is_noti_to_slack
