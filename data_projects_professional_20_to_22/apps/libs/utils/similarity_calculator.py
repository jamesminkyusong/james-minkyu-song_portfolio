from datetime import datetime

import pandas as pd
import re
import textdistance

from libs.utils.text_utils import TextUtils


app_name = 'similarity_calculator'
similarity_f = lambda text1, text2: textdistance.sorensen_dice.normalized_similarity(text1.lower(), text2.lower())
# similarity_f = lambda text1, text2: textdistance.levenshtein.normalized_similarity(text1.lower(), text2.lower())


class SimilarityCalculator:
	def calc_two_cols(self, col_name1, col_name2):
		print('{} [INFO][{}.calc_two_cols] Comparing {} and {} ...'.format(str(datetime.now()), app_name, col_name1, col_name2))
	
		similarities = []
		for row_i, text in enumerate(zip(self.__df[col_name1], self.__df[col_name2])):
			similarity = similarity_f(str(text[0]), str(text[1]))
			similarities += [similarity]

			if (h_i := row_i+1) % 100 == 0 or h_i == len(self.__df):
				print('{} [INFO][{}.calc_two_cols] {:,}/{:,} rows compared'.format(str(datetime.now()), app_name, h_i, len(self.__df)))
	
		self.__df.insert(
			len(self.__df.columns),
			"similarity_{}_{}".format(col_name1, col_name2),
			similarities)


	def __calc(self, batch_name, df, min_similarity, sid_col_i, text_col_i, similar_sid_col_i, similar_text_col_i, similarity_col_i, is_full_scan=False, sort_col_name=None, max_compare_count=0):
		if sort_col_name:
			df.sort_values(by=sort_col_name, inplace=True)

		for row_i in range(len(df)):
			base_sid = df.iloc[row_i, sid_col_i]
			base_text = df.iloc[row_i, text_col_i]

			if max_compare_count > 0:
				compare_range = range(row_i+1, min(row_i+1+max_compare_count, len(df)))
			else:
				compare_range = range(row_i+1, len(df))

			for compare_row_i in compare_range:
				compare_text = df.iloc[compare_row_i, text_col_i]

				similarity = similarity_f(base_text, compare_text)
				if similarity < min_similarity:
					if is_full_scan:
						continue
					else:
						break

				compare_sid = df.iloc[compare_row_i, sid_col_i]
				if base_sid > compare_sid:
					if similarity > df.iloc[row_i, similarity_col_i] and compare_sid != df.iloc[row_i, sid_col_i]:
						df.iloc[row_i, similar_sid_col_i] = compare_sid
						df.iloc[row_i, similar_text_col_i] = compare_text
						df.iloc[row_i, similarity_col_i] = similarity
				else:
					if similarity > df.iloc[compare_row_i, similarity_col_i] and base_sid != df.iloc[compare_row_i, sid_col_i]:
						df.iloc[compare_row_i, similar_sid_col_i] = base_sid
						df.iloc[compare_row_i, similar_text_col_i] = base_text
						df.iloc[compare_row_i, similarity_col_i] = similarity
	
			if (h_i := row_i+1) % 100 == 0 or h_i == len(df):
				print('{} [INFO][{}.calc][{}] {:,}/{:,} rows compared'.format(str(datetime.now()), app_name, batch_name, h_i, len(df)))


	"""
	eg.
	sid |  ko | sid_sim_ko | sim_ko | similarity
	----+-----+------------+--------+-----------
	  1 |     |         -1 |        |          0
	  2 |     |          3 |        |       0.95
	  3 |     |         -1 |        |          0
	  4 |     |          5 |        |       0.90
	  5 |     |         -1 |        |          0
	... | ... |        ... |    ... |        ...
	"""
	def get_similarity_marked_df(self, col_name, sid_col_name='sid', is_full_scan=False, min_similarity=0.9):
		print('{} [INFO][{}.get_similarity_marked_df][{}] Calculating simiarities (min: {}) ...'.format(str(datetime.now()), app_name, col_name, min_similarity))
		return self.__calc_in_one_col(
			col_name,
			sid_col_name,
			False,
			is_full_scan,
			min_similarity)


	"""
	eg.
	sid |  ko | sid_sim_ko | sim_ko | similarity
	----+-----+------------+--------+-----------
	  2 |     |          3 |        |       0.95
	  4 |     |          5 |        |       0.90
	... | ... |        ... |    ... |        ...
	"""
	def get_similar_df(self, col_name, sid_col_name='sid', is_full_scan=False, min_similarity=0.9, is_vertical_output=False):
		print('{} [INFO][{}.get_similar_df][{}] Calculating simiarities (min: {}) ...'.format(str(datetime.now()), app_name, col_name, min_similarity))
		similar_df = self.__calc_in_one_col(
			col_name,
			sid_col_name,
			True,
			is_full_scan,
			min_similarity)

		if is_vertical_output:
			similar_df = self.__convert_to_vertical_df(similar_df)

		return similar_df


	def __calc_in_one_col(self, col_name, sid_col_name='sid', is_similar_rows_only=True, is_full_scan=False, min_similarity=0.9):
		if sid_col_name not in list(self.__df.columns):
			similar_df = self.__df[[col_name]]
			self.add_sid(similar_df)
		else:
			similar_df = self.__df[[sid_col_name] + [col_name]]
		similar_df.insert(0, 'row_i', list(range(len(similar_df))))

		similar_df.columns = ['row_i', sid_col_name, col_name]
		similar_df[f'sid_sim_{col_name}'] = [-1] * len(similar_df)
		similar_df[f'sim_{col_name}'] = [''] * len(similar_df)
		similar_df[f'similarity'] = [0] * len(similar_df)

		sid_col_i, text_col_i, similar_sid_col_i, similar_text_col_i, similarity_col_i = list(range(1, 6))
		reassembled_text_col_name = 'reassembled_' + col_name

		text_utils = TextUtils('text_utils')
		if col_name == 'zh':
			re_lang = re.compile(r'[\u4e00-\u9fff]')
		else:
			re_lang = text_utils.get_re_lang(col_name)

		batch_i = 0
		if is_full_scan:
			batch_i += 1
			similar_df[reassembled_text_col_name] = similar_df[col_name].apply(lambda text: ' '.join(re_lang.findall(str(text))))
			self.__calc(
				f'batch #{batch_i}',
				similar_df,
				min_similarity,
				*[sid_col_i, text_col_i, similar_sid_col_i, similar_text_col_i, similarity_col_i],
				is_full_scan=True)
		else:
			if re_lang:
				if col_name in ['ja', 'zh']:
					batch_i += 1
					similar_df[reassembled_text_col_name] = similar_df[col_name].apply(lambda text: ''.join(sorted(re_lang.findall(str(text)))))
					self.__calc(
						f'batch #{batch_i}',
						similar_df,
						min_similarity,
						*[sid_col_i, text_col_i, similar_sid_col_i, similar_text_col_i, similarity_col_i],
						sort_col_name=reassembled_text_col_name)
				else:
					batch_i += 1
					similar_df[reassembled_text_col_name] = similar_df[col_name].apply(lambda text: ' '.join(sorted(re_lang.findall(str(text)))))
					self.__calc(
						f'batch #{batch_i}',
						similar_df,
						min_similarity,
						*[sid_col_i, text_col_i, similar_sid_col_i, similar_text_col_i, similarity_col_i],
						sort_col_name=reassembled_text_col_name)
		
					batch_i += 1
					similar_df[reassembled_text_col_name] = similar_df[col_name].apply(lambda text: ' '.join(re_lang.findall(str(text))))
					self.__calc(
						f'batch #{batch_i}',
						similar_df,
						min_similarity,
						*[sid_col_i, text_col_i, similar_sid_col_i, similar_text_col_i, similarity_col_i])
	
			batch_i += 1
			self.__calc(
				f'batch #{batch_i}',
				similar_df,
				min_similarity,
				*[sid_col_i, text_col_i, similar_sid_col_i, similar_text_col_i, similarity_col_i],
				sort_col_name=col_name)
	
			batch_i += 1
			self.__calc(
				f'batch #{batch_i}',
				similar_df,
				min_similarity,
				*[sid_col_i, text_col_i, similar_sid_col_i, similar_text_col_i, similarity_col_i],
				sort_col_name=sid_col_name,
				max_compare_count=100)

		similar_df.drop(columns=reassembled_text_col_name, inplace=True)
		if is_similar_rows_only:
			similar_df = similar_df[similar_df['similarity'] > 0]
			similar_df.sort_values(by='similarity', ascending=False, inplace=True)
			similar_count = len(similar_df)
		else:
			similar_df.sort_values(by='row_i', ascending=False, inplace=True)
			similar_count = len(similar_df[similar_df[f'sid_sim_{col_name}'] > 0])
		similar_df.drop(columns='row_i', inplace=True)

		print('{} [INFO][{}.calc_in_one_col][{}] Similar pairs: {:,}'.format(str(datetime.now()), app_name, col_name, len(similar_df)))
		return similar_df


	"""
	eg.
	sid |  ko | sid_sim_ko | sim_ko | similarity   =>   group_id | sid | ko | similarity
	----+-----+------------+--------+-----------        ---------+-----+----+-----------
	  2 |     |          3 |        |       0.95               1 |   2 |    |       0.95
	  4 |     |          5 |        |       0.90               1 |   3 |    |       0.95
	... | ... |        ... |    ... |        ...               2 |   4 |    |       0.90
	                                                           2 |   5 |    |       0.90
	                                                    ........ | ... | .. | ..........
	"""
	def __convert_to_vertical_df(self, df):
		row_i = 0
		new_rows = []
		for _, row in df.iterrows():
			row_i += 1
			new_rows += [[row_i, row[0], row[1], row[4]]]
			new_rows += [[row_i, row[2], row[3], row[4]]]

		df_col_names = list(df.columns)
		return pd.DataFrame(data=new_rows, columns=['group_id', df_col_names[0], df_col_names[1], df_col_names[4]])


	def __init__(self, name, df):
		self.name = name
		self.__df = df
