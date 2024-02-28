#!../../../bin/python3

from datetime import datetime
import os
import pickle

from nltk.tokenize import word_tokenize
import gensim
import pandas as pd

from cmd_args_similarity import CMDArgsSimilarity
from libs.utils.alert import Alert
from libs.utils.df_utils import DFUtils
from libs.utils.reader import Reader


def get_df(path, count, input_file, sheet_index, col_indices, col_names, start_row, lang_codes):
	print('{} [INFO][check_similarity.get_df] Reading from {} ...'.format(str(datetime.now()), input_file))

	reader = Reader('reader', lang_codes)
	df = reader.get_df('%s/%s' % (path, input_file), sheet_index, col_indices, col_names, start_row, nrows=count)

	print('{} [INFO][check_similarity.get_df] {:,} rows fetched in {}'.format(str(datetime.now()), len(df), input_file))
	return df


def get_tfidf_files(df, lang_col_name):
	dictionary_file = f'./{lang_col_name}_dict.bin'
	tfidf_file = f'./{lang_col_name}_tfidf.bin'
	index_file = f'./{lang_col_name}_index.bin'

	if all([os.path.exists(dictionary_file), os.path.exists(tfidf_file), os.path.exists(f'{index_file}.0')]):
		print('FILE FOUND!')
		with open(dictionary_file, 'rb') as f:
			dictionary = pickle.load(f)
		with open(tfidf_file, 'rb') as f:
			tfidf = pickle.load(f)
		similarities = gensim.similarities.Similarity.load(f'{index_file}.0')
	else:
		print('FILE NOT FOUND!!!')
		tokenized_texts = [[w.lower() for w in word_tokenize(text)] for text in df[lang_col_name].values]
		dictionary = gensim.corpora.Dictionary(tokenized_texts)
		bows = [dictionary.doc2bow(tokenized_text) for tokenized_text in tokenized_texts]
		tfidf = gensim.models.TfidfModel(bows)

		with open(dictionary_file, 'wb') as f:
			pickle.dump(dictionary, f)
		with open(tfidf_file, 'wb') as f:
			pickle.dump(tfidf, f)
		similarities = gensim.similarities.Similarity(index_file, tfidf[bows], num_features=len(dictionary))

	return dictionary, tfidf, similarities


def get_similar_df(df, id_col_index, lang_col_index, lang_col_name, similarity):
	dictionary, tfidf, similarities = get_tfidf_files(df, lang_col_name)

	similar_rows = []
	for row_index, row in enumerate(df.values):
		tokenized_text = [w.lower() for w in word_tokenize(row[lang_col_index])]
		text_bow = dictionary.doc2bow(tokenized_text)
		text_tfidf = tfidf[text_bow]

		sim_scores = zip(range(len(similarities)), similarities[text_tfidf])
		sim_scores = [sim_score for row_index_2, sim_score in enumerate(sim_scores) if row_index_2 > row_index and sim_score[1] >= similarity]
		sim_scores = sorted(sim_scores, key=lambda sim_score: sim_score[1], reverse=True)

		for sim_score in sim_scores:
			id1 = row[id_col_index]
			id2 = df.iloc[sim_score[0], id_col_index]
			if id1 != id2:
				similar_rows += [[id1, row[lang_col_index], id2, df.iloc[sim_score[0], lang_col_index], sim_score[1]]]

		if (row_index + 1) % 1000 == 0:
			print('{} [INFO][check_similarity.get_similar_df] {:,}/{:,} rows checked'.format(str(datetime.now()), row_index+1, len(df)))

	similar_df = pd.DataFrame(data=similar_rows, columns=['id1', 'text1', 'id2', 'text2', 'similarity'])

	return similar_df


def notify(level, message, is_noti_to_slack):
	level = level.upper()
	print('%s [%s]%s' % (str(datetime.now()), level, message))
	if is_noti_to_slack:
		alert.send(level, '`[%s]` %s' % (level, message))


def main():
	args_similarity = CMDArgsSimilarity('args', ['path', 'output_file', 'input_files', 'id_col_name', 'lang_col_name'])
	args = args_similarity.values

	if args.is_noti_to_slack:
		global alert
		alert = Alert('alert')

	lang_codes = ['ar', 'de', 'en', 'es', 'fr', 'hi', 'id', 'ja', 'ko', 'ms', 'pt', 'ru', 'th', 'tl', 'tr', 'vi', 'zh']

	dfs = []
	for input_file in args.input_files:
		df = get_df(args.path, args.count, input_file, args.sheet_index, args.col_indices, args.col_names, args.start_row, lang_codes)
		dfs += [df]

	df_utils = DFUtils('df_utils')
	df = df_utils.merge(dfs) if len(dfs) > 1 else dfs[0]

	id_col_index = args.col_names.index(args.id_col_name)
	lang_col_index = args.col_names.index(args.lang_col_name)
	similar_df = get_similar_df(df, id_col_index, lang_col_index, args.lang_col_name, args.min_similarity)
	similar_df_len = len(similar_df)
	if similar_df_len > 0:
		if args.is_add_sid:
			df_utils.add_sid(similar_df)
		df_utils.save(similar_df, args.path, args.output_file)

	message = '[check_similarity.main] Similar {:,} rows saved in {}'.format(similar_df_len, args.output_file)
	notify('info', message, args.is_noti_to_slack)


if __name__ == '__main__':
	main()
