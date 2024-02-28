from datetime import datetime
import glob
import os
import random
import re
import unicodedata as ud

import pandas as pd
import spacy
import textdistance

from libs.utils.df_utils import DFUtils
from libs.utils.mt import MT
from libs.utils.reader import Reader
from libs.utils.similarity_calculator import SimilarityCalculator
from libs.utils.text_utils import TextUtils


app_name = 'quality_filter'
percent = lambda count, all_count: '{}%'.format(int(count*100 / all_count))
# similarity_f = lambda text1, text2: textdistance.damerau_levenshtein.normalized_similarity(text1.lower(), text2.lower())
# similarity_f = lambda text1, text2: textdistance.levenshtein.normalized_similarity(text1.lower(), text2.lower())
similarity_f = lambda text1, text2: textdistance.sorensen_dice.normalized_similarity(text1.lower(), text2.lower())


class QualityFilter:
	__tokenizable_lang_codes = {
		'de': 'de_core_news_sm',
		'en': 'en_core_web_sm',
		'es': 'es_core_news_sm',
		'ja': 'ja_core_news_sm',
		'pt': 'pt_core_news_sm'
	}

	__mono_corpora_path = os.environ['CORPUSPATH'] + '/mono'
	__profanity_path = os.environ['CORPUSPATH'] + '/profanity_words'
	__profanity_lang_codes = ['de', 'en', 'es', 'fr', 'id', 'it', 'ja', 'ko', 'pt', 'ru', 'tr']

	__filter_col_names = []
	__filter_df = pd.DataFrame()


	def __mark_duplicates(self, df, col_names):
		filter_col_names = []
		filter_df = pd.DataFrame()

		for col_name in col_names:
			print('{} [INFO][{}.mark_duplicates][{}] Dropping duplicates ...'.format(str(datetime.now()), app_name, col_name))
			filter_col_name = f'dup_{col_name}'
			filter_col_names += [filter_col_name]
			filter_df[filter_col_name] = ~df.duplicated(subset=col_name)
			duplicates_count = len(df[~filter_df[filter_col_name]])
			print('{} [INFO][{}.mark_duplicates][{}] Mark as bad: {:,} ({})'.format(str(datetime.now()), app_name, col_name, duplicates_count, percent(duplicates_count, len(df))))

		filter_df.columns = filter_col_names
		return filter_col_names, filter_df


	def __mark_translated(self, df, col_names):
		print('{} [INFO][{}.mark_translated][{}] Dropping not-translated texts ...'.format(str(datetime.now()), app_name, ', '.join(col_names)))

		col_indices = [list(df.columns).index(col_name) for col_name in col_names]
		cols_count = len(col_names)
		filter_col_names = ['translated']

		rows = []
		for row in df.values:
			is_translated = cols_count == len(set([text.replace(' ', '').lower() if isinstance((text := row[col_i]), str) else str(text) for col_i in col_indices]))
			rows += [is_translated]
		filter_df = pd.DataFrame(data=rows, columns=filter_col_names)
		not_translated_count = (~filter_df[filter_col_names[0]]).sum()

		print('{} [INFO][{}.mark_translated][{}] Mark as bad: {:,} ({})'.format(str(datetime.now()), app_name, ', '.join(col_names), not_translated_count, percent(not_translated_count, len(df))))
		return filter_col_names, filter_df


	def __mark_by_filter_using_two_cols(self, df, filter_df, col_names, filter_col_name, two_cols_filter):
		print('{} [INFO][{}.mark_by_filters][{}] Filtering by {} ...'.format(str(datetime.now()), app_name, ', '.join(col_names[0:2]), filter_col_name))
		filter_df[filter_col_name] = df[[col_names[0], col_names[1]]].apply(lambda x: two_cols_filter(*x), axis=1)
		filtered_count = len(df[filter_df[filter_col_name] != 1])
		print('{} [INFO][{}.mark_by_filters][{}] Mark as bad: {:,} ({})'.format(str(datetime.now()), app_name, ', '.join(col_names[0:2]), filtered_count, percent(filtered_count, len(df))))


	def __mark_by_filters(self, df, col_names, max_words_count, min_words_count, max_chars_count, min_chars_count, max_len_ratio, is_drop_if_email, is_drop_if_tel, is_drop_if_url, is_drop_if_alphabet, is_drop_if_chinese, is_drop_if_korean, is_drop_if_no_korean, is_drop_if_number):
		filter_col_names = []
		filter_df = pd.DataFrame()

		prefixes = []
		filter_funcs = []

		text_utils = TextUtils('text_utils')

		# filter 1: Check whether a text is string or not
		str_filter = lambda text: isinstance(text, str)
		prefixes += ['str']
		filter_funcs += [str_filter]
	
		# filter 2: Check whether a text has wrong characters or not
		regex1 = re.compile('%[a-zA-Z(]')
		regex2 = re.compile('^[a-zA-Z0-9\'"$]')
		common_wrong_char_filter = lambda text: str_filter(text) \
			and not bool(regex1.search(text)) \
			and "%d" not in text \
			and "%s" not in text \
			and text.count('"') % 2 == 0
		en_wrong_char_filter = lambda text: common_wrong_char_filter(text) \
			and bool(regex2.search(text))
		wrong_char_filter = lambda lang_code: en_wrong_char_filter if lang_code == 'en' else common_wrong_char_filter
		prefixes += ['no_wrong_char']
		filter_funcs += [wrong_char_filter]

		# filter 3: Add filter to drop a text if it has an email
		if is_drop_if_email:
			regex_email = re.compile('[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
			email_filter = lambda text: not (isinstance(text, str) and bool(regex_email.search(text)))
			prefixes += ['no_email']
			filter_funcs += [email_filter]

		# filter 4: Add filter to drop a text if it has an telephone number
		if is_drop_if_tel:
			regex_tel = re.compile('(\+\d{1,2}\s)?\(?\d{2,3}\)?[\s.-]\d{3,4}[\s.-]\d{4}$')
			tel_filter = lambda text: not (isinstance(text, str) and bool(regex_tel.search(text)))
			prefixes += ['no_tel']
			filter_funcs += [tel_filter]

		# filter 5: Add filter to drop a text if it has an url
		if is_drop_if_url:
			regex_url = re.compile('http[s]?://')
			url_filter = lambda text: not (isinstance(text, str) and (bool(regex_url.search(text)) or ('.com' in text)))
			prefixes += ['no_url']
			filter_funcs += [url_filter]

		# filter 6: Add filter to drop a text if it has an alphabet
		if is_drop_if_alphabet:
			alphabet_filter = lambda text: len(re.sub('EMAIL|ID|NUMBER|TEL|URL', '', re.sub('[^a-zA-Z]+', '', str(text)))) <= 0
			prefixes += ['no_alphabet']
			filter_funcs += [alphabet_filter]

		# filter 7: Add filter to drop a text if it has an Chinese
		if is_drop_if_chinese:
			regex_chinese = text_utils.get_re_lang('zh')
			chinese_filter = lambda text: not (isinstance(text, str) and bool(regex_chinese.search(text)))
			prefixes += ['no_chinese']
			filter_funcs += [chinese_filter]

		# filter 8: Add filter to drop a text if it has an Korean
		if is_drop_if_korean:
			regex_korean = text_utils.get_re_lang('ko')
			korean_filter = lambda text: not (isinstance(text, str) and bool(regex_korean.search(text)))
			prefixes += ['no_korean']
			filter_funcs += [korean_filter]

		# filter 9: Add filter to drop a text if it has no Korean
		if is_drop_if_no_korean:
			regex_korean = text_utils.get_re_lang('ko')
			no_korean_filter = lambda text: not (isinstance(text, str) and not bool(regex_korean.search(text)))
			prefixes += ['korean']
			filter_funcs += [no_korean_filter]

		# filter 10: Add filter to drop a text if it has an number
		if is_drop_if_number:
			regex_number = re.compile('[0-9]+')
			prefixes += ['no_number']
			number_filter = lambda text: not (isinstance(text, str) and bool(regex_number.search(text)))
			filter_funcs += [number_filter]

		# filter 11: Check whether a text contains a html tag
		# html_filter = lambda text: isinstance(text, str) and (text.split()[0] not in ['P']) and (text.split()[-1] not in ['/p.'])
		re_url_encoding = re.compile('&[a-z]+;')
		html_filter = lambda text: isinstance(text, str) and len(re_url_encoding.findall(text)) <= 0
		prefixes += ['no_html']
		filter_funcs += [html_filter]

		# filter 12: Check whether a text is too short/long or not
		words_count_filter = lambda text: str_filter(text) and min_words_count <= len(text.split(' ')) <= max_words_count
		chars_count_filter = lambda text: str_filter(text) and min_chars_count <= len(text) <= max_chars_count
		th_chars_count_filter = lambda text: str_filter(text) and min_chars_count <= sum(1 for cp in ''.join(text_utils.get_re_lang('th').findall(text)) if ud.category(cp)[0] != 'M') <= max_chars_count
		length_filter = lambda lang_code: chars_count_filter if lang_code in ['ja', 'zh'] else th_chars_count_filter if lang_code == 'th' else words_count_filter
		prefixes += ['length']
		filter_funcs += [length_filter]

		# filter 13: Check whether a text has profanity words or not
		if self.__filters.is_check_profanity and any([col_name for col_name in col_names if col_name in self.__profanity_lang_codes]):
			profanity_words = []
			profanity_filter = lambda text: not (isinstance(text, str) and any([any([profanity_word for profanity_word in profanity_words if profanity_word == token]) for token in text.split(' ')]))
			prefixes += ['no_profanity']
			filter_funcs += [profanity_filter]

		for prefix, parent_filter_func in zip(prefixes, filter_funcs):
			for col_name in col_names:
				if prefix in ['no_wrong_char', 'length']:
					filter_func = parent_filter_func(col_name)
				elif prefix == 'no_profanity':
					with open(f'{self.__profanity_path}/words_{col_name}.txt') as f:
						profanity_words = [line.strip() for line in f.readlines()]
					filter_func = parent_filter_func
				elif prefix == 'no_alphabet' and col_name in ['de', 'en', 'es', 'fr', 'id', 'it', 'ms', 'pt', 'tl', 'tr']:
					continue
				elif prefix == 'no_chinese' and col_name in ['ja', 'zh']:
					continue
				elif prefix == 'no_korean' and col_name == 'ko':
					continue
				elif prefix == 'korean' and col_name != 'ko':
					continue
				else:
					filter_func = parent_filter_func
	
				print('{} [INFO][{}.mark_by_filters][{}] Filtering by {} ...'.format(str(datetime.now()), app_name, col_name, prefix))
				filter_col_name = f'{prefix}_{col_name}'
				filter_col_names += [filter_col_name]
				filter_df[filter_col_name] = df[col_name].apply(filter_func)
				filtered_count = len(df[filter_df[filter_col_name] != 1])
				print('{} [INFO][{}.mark_by_filters][{}] Mark as bad: {:,} ({})'.format(str(datetime.now()), app_name, col_name, filtered_count, percent(filtered_count, len(df))))

		# filter 14: Check whether text2 is too short or long compared with text1
		if max_len_ratio > 0 and len(col_names) >= 2:
			max_len_ratio_filter = lambda text1, text2: 1/max_len_ratio <= len(text1)/len(text2) <= max_len_ratio
			filter_col_name = 'max_len_ratio'
			filter_col_names += [filter_col_name]
			self.__mark_by_filter_using_two_cols(df, filter_df, col_names, filter_col_name, max_len_ratio_filter)

		# filter 13: Check whether text1 and text2 have same english words
		if self.__filters.is_compare_en_words and len(col_names) >= 2 and 'en' not in col_names:
			re_en = re.compile('[a-zA-Z][a-zA-Z0-9]+')
			en_words_filter = lambda text1, text2: set(re_en.findall(text1)) == set(re_en.findall(text2))
			filter_col_name = 'same_en_words'
			filter_col_names += [filter_col_name]
			self.__mark_by_filter_using_two_cols(df, filter_df, col_names, filter_col_name, en_words_filter)

		filter_df.columns = filter_col_names
		return filter_col_names, filter_df


	def __mark_by_nlp(self, df, col_names):
		prefixes = []
		filter_funcs = []

		# filter 1: Check whether a text has verb or not
		if self.__filters.is_check_verb:
			verb_poses = ['AUX', 'VERB']
			verb_filter = lambda document: any([verb_pos in [token.pos_ for token in document] for verb_pos in verb_poses])
			prefixes += ['verb']
			filter_funcs += [verb_filter]

		# filter 2: Check whether a text has one sentence or not
		if self.__filters.is_check_one_text:
			one_text_filter = lambda document: True if (texts_count := len(list(document.sents))) == 1 else False
			prefixes += ['one_text']
			filter_funcs += [one_text_filter]

		nlp_col_names = [col_name for col_name in col_names if col_name in self.__tokenizable_lang_codes.keys()]
		nlps = {col_name: spacy.load(self.__tokenizable_lang_codes[col_name]) for col_name in nlp_col_names}
		nlp_df = pd.DataFrame()
		sliced_nlp_df = pd.DataFrame()
		df_utils = DFUtils('df_utils')
		for col_name in nlp_col_names:
			print('{} [INFO][{}.mark_by_nlp][{}] Loading SpaCy ...'.format(str(datetime.now()), app_name, col_name))
			nlp = nlps[col_name]
			print('{} [INFO][{}.mark_by_nlp][{}] Tokenizing ...'.format(str(datetime.now()), app_name, col_name))
			nlp_df[col_name] = df[col_name].apply(lambda text: nlp(text) if isinstance(text, str) else nlp(str(text)))

		filter_df = pd.DataFrame()
		filter_col_names = []
		for prefix, filter_func in zip(prefixes, filter_funcs):
			for col_name in nlp_col_names:
				print('{} [INFO][{}.mark_by_nlp][{}] Filtering by {} ...'.format(str(datetime.now()), app_name, col_name, prefix))
				filter_col_name = f'{prefix}_{col_name}'
				filter_col_names += [filter_col_name]
				filter_df[filter_col_name] = nlp_df[col_name].apply(filter_func)
				filtered_count = len(df[filter_df[filter_col_name] != 1])
				print('{} [INFO][{}.mark_by_nlp][{}] Mark as bad: {:,} ({})'.format(str(datetime.now()), app_name, col_name, filtered_count, percent(filtered_count, len(df))))
	
		filter_df.columns = filter_col_names
		return filter_col_names, filter_df


	def __mark_similarity(self, df, check_col_name, sid_col_name, max_similarity):
		print('{} [INFO][{}.mark_similarity][{}] Calculating simiarities (max similarity: {}) ...'.format(str(datetime.now()), app_name, check_col_name, max_similarity))
		filter_col_names = [f'no_similar_{check_col_name}']

		similarity_calculator = SimilarityCalculator('similarity_calculator', df)
		similar_df = similarity_calculator.get_similarity_marked_df(check_col_name, sid_col_name=sid_col_name)[[f'sid_sim_{check_col_name}']]
		similar_df.columns = filter_col_names

		filtered_count = len(similar_df[similar_df[filter_col_names[0]] > -1])
		print('{} [INFO][{}.mark_similarity][{}] Mark as bad: {:,} ({})'.format(str(datetime.now()), app_name, check_col_name, filtered_count, percent(filtered_count, len(df))))
		return filter_col_names, similar_df


	def __get_df(self, path, input_file, col_indices, col_names, lang_codes):
		reader = Reader('reader', lang_codes)
		df = reader.get_df('%s/%s' % (path, input_file), 0, col_indices, col_names, 1)

		return df


	def __check_in_flitto(self, df, col_name, lang_codes):
		print('{} [INFO][{}.check_in_flitto][{}] Searching in Flitto ...'.format(str(datetime.now()), app_name, col_name))
		flitto_files = sorted([filename.rsplit('/', 1)[-1] for filename in glob.glob(f'{self.__mono_corpora_path}/mono_{col_name}*.xlsx')])
		if not flitto_files:
			return None, None

		filter_col_names = [f'not_have_{col_name}']
		filter_df = pd.DataFrame(data=[True] * len(df), columns=filter_col_names)

		for flitto_file in flitto_files:
			flitto_df = self.__get_df(self.__mono_corpora_path, flitto_file, [2, 3], ['corpus_id', col_name], lang_codes)
			dup_df = df[col_name].apply(lambda text: matched[0] if (matched := [row[0] for row in flitto_df.values if text == row[1]]) else True)
			filter_df[filter_col_names[0]] = filter_df[filter_col_names[0]].combine(dup_df, lambda first, second: first if int(first) > 1 else (second if int(second) > 1 else True))
	
		filter_df.columns = filter_col_names
		filtered_count = len(df[filter_df[filter_col_names[0]] > 1])
		print('{} [INFO][{}.check_in_flitto][{}] Mark as bad: {:,} ({})'.format(str(datetime.now()), app_name, col_name, filtered_count, percent(filtered_count, len(df))))
		return filter_col_names, filter_df


	def __filter_all_passed(self, filter_df, filter_col_names):
		is_similar_col = lambda col: 'similar' in col

		all_passed_df = filter_df[filter_col_names[0]]
		if len(filter_col_names) == 1 and is_similar_col(filter_col_names[0]):
			all_passed_df = all_passed_df.apply(lambda x: x == -1)
		else:
			for filter_col_name in filter_col_names[1:]:
				passed_df = filter_df[filter_col_name]
				true_value = -1 if is_similar_col(filter_col_name) else 1
				all_passed_df = all_passed_df.combine(passed_df, lambda first, second: first and (int(second) == true_value))

		return all_passed_df


	def __append(self, filter_col_names, filter_df):
		if filter_col_names:
			self.__filter_col_names += filter_col_names
			self.__filter_df = pd.concat([self.__filter_df, filter_df], axis=1)


	def __drop_all_passed_cols(self):
		col_i = 0
		while col_i < len(self.__filter_col_names):
			col_name = self.__filter_col_names[col_i]
			if self.__filter_df[col_name].apply(lambda x: False if x == 1 else True).sum() == 0:
				print('{} [INFO][{}.drop_all_passed_cols] Drop all-passed column: {}'.format(str(datetime.now()), app_name, col_name))
				self.__filter_df.drop(columns=[col_name], inplace=True)
				del self.__filter_col_names[col_i]
			else:
				col_i += 1


	def translate_df(self, config, df, mt_sample_ratio, src_lang_code, dst_lang_code):
		print('{} [INFO][{}.translate_df] Translating {} to {} ...'.format(str(datetime.now()), app_name, src_lang_code, dst_lang_code))
		indices = list(range(len(df)))
		random.shuffle(indices)
		indices = sorted(indices[:int(len(df) / 100 * mt_sample_ratio)])
		mt_df = df.iloc[indices, :]
		mt_df.reset_index(inplace=True)

		src_text_col_i = list(mt_df.columns).index(src_lang_code)
		dst_text_col_i = list(mt_df.columns).index(dst_lang_code)
		translated_texts = []
		similarities = []

		mt = MT('mt', config)
		for i, row in mt_df.iterrows():
			src_text = row[src_text_col_i]
			translated_text = mt.send(src_lang_code, dst_lang_code, src_text)
			translated_texts.append(translated_text)
			similarity = similarity_f(row[dst_text_col_i], translated_text)
			similarities.append(similarity)
			if (i + 1) % 100 == 0:
				print('{} [INFO][{}.translate_df] {:,}/{:,} rows translated'.format(str(datetime.now()), app_name, i+1, len(mt_df)))

		mt_col_name = f'mt_{dst_lang_code}'
		similarity_col_name = f'similarity_{dst_lang_code}'
		mt_df.insert(len(mt_df.columns), mt_col_name, translated_texts)
		mt_df.insert(len(mt_df.columns), similarity_col_name, similarities)

		exactly_same_count = len(mt_df[mt_df[similarity_col_name] == 1])
		avg_similarity = mt_df[similarity_col_name].mean()
		print('{} [INFO][{}.translate_df] {:,} texts are exactly same and average similarity is {}'.format(str(datetime.now()), app_name, exactly_same_count, avg_similarity))

		return mt_df


	def execute(self, df, col_names):
		lang_col_names = [col_name for col_name in col_names if col_name in self.__lang_codes]

		filter_col_names, filter_df = self.__mark_duplicates(df, lang_col_names)
		self.__append(filter_col_names, filter_df)

		if len(lang_col_names) >= 2:
			filter_col_names, filter_df = self.__mark_translated(df, lang_col_names)
			self.__append(filter_col_names, filter_df)

		filter_col_names, filter_df = self.__mark_by_filters(
			df,
			lang_col_names,
			self.__filters.max_words_count,
			self.__filters.min_words_count,
			self.__filters.max_chars_count,
			self.__filters.min_chars_count,
			self.__filters.max_len_ratio,
			self.__filters.is_drop_if_email,
			self.__filters.is_drop_if_tel,
			self.__filters.is_drop_if_url,
			self.__filters.is_drop_if_alphabet,
			self.__filters.is_drop_if_chinese,
			self.__filters.is_drop_if_korean,
			self.__filters.is_drop_if_no_korean,
			self.__filters.is_drop_if_number)
		self.__append(filter_col_names, filter_df)

		if any([self.__filters.is_check_verb, self.__filters.is_check_one_text]) \
			and any([col_name for col_name in lang_col_names if col_name in self.__tokenizable_lang_codes.keys()]):
			filter_col_names, filter_df = self.__mark_by_nlp(df, col_names)
			self.__append(filter_col_names, filter_df)

		if self.__filters.is_check_similarity:
			for lang_col_name in lang_col_names:
				filter_col_names, filter_df = self.__mark_similarity(
					df,
					lang_col_name,
					self.__filters.similarity_sid_col_name,
					self.__filters.max_similarity)
				self.__append(filter_col_names, filter_df)

		if self.__filters.is_check_in_flitto:
			for col_name in lang_col_names:
				filter_col_names, filter_df = self.__check_in_flitto(df, col_name, self.__lang_codes)
				self.__append(filter_col_names, filter_df)

		self.__drop_all_passed_cols()

		if len(self.__filter_col_names) == 0:
			not_bad_df = df
			bad_df = pd.DataFrame()
		else:
			passed_df = self.__filter_all_passed(self.__filter_df, self.__filter_col_names)
			not_bad_df = df[passed_df]
			if self.__filters.is_add_filter_result:
				df = pd.concat([df, self.__filter_df], axis=1)
			bad_df = df[~passed_df]
	
		not_bad_count = len(not_bad_df)
		bad_count = len(bad_df)
		all_count = len(df)
		print('{} [INFO][{}.execute] Marked as not bad: {:,} ({}) / bad: {:,} ({})'.format(str(datetime.now()), app_name, not_bad_count, percent(not_bad_count, all_count), bad_count, percent(bad_count, all_count)))

		return not_bad_df, bad_df


	def save_df(self, df, category, path, max_rows_in_file, input_file):
		output_file = f'_{category}.'.join(input_file.rsplit('.', 1))
		df_utils = DFUtils('df_utils')
		df_utils.save(df, path, output_file, max_rows_in_file=max_rows_in_file)
		print('{} [INFO][{}.save_df][{}] Saved rows: {:,} in {}'.format(str(datetime.now()), app_name, category, len(df), output_file))


	def save_similarity_df(self, df, check_col_name, sid_col_name, col_names, path, max_rows_in_file, input_file):
		if sid_col_name not in df.columns:
			sid_col_name = "temp_sid"
			df.insert(0, sid_col_name, list(range(2, 2+len(df))))

		index_f = lambda col_name: list(df.columns).index(col_name)

		sid_col_i = index_f(sid_col_name)
		base_text_i = index_f(check_col_name)
		compare_text_i = list(self.__filter_df.columns).index(f'no_similar_{check_col_name}')
		index_of_sid_f = lambda sid: df[df[sid_col_name] == base_sid].index.to_list()[0]
		pair_langs = list(filter(lambda x: x != check_col_name and x in self.__lang_codes, col_names))
		pair_text_i = index_f(pair_langs[0]) if len(pair_langs) > 0 else None

		rows = []
		for index, row in enumerate(self.__filter_df.values):
			if (base_sid := int(row[compare_text_i])) <= 1:
				continue

			compare_sid = df.iloc[index, sid_col_i]
			base_text = df.iloc[index_of_sid_f(base_sid), base_text_i]
			compare_text = df.iloc[index, base_text_i]
			similarity = similarity_f(base_text, compare_text)
			if pair_text_i:
				pair_of_base_text = df.iloc[index_of_sid_f(base_sid), pair_text_i]
				pair_of_compare_text = df.iloc[index, pair_text_i]
				similarity_of_pair = similarity_f(pair_of_base_text, pair_of_compare_text)
				rows += [[base_sid, compare_sid, base_text, compare_text, similarity, pair_of_base_text, pair_of_compare_text, similarity_of_pair]]
			else:
				rows += [[base_sid, compare_sid, base_text, compare_text, similarity]]

		if len(rows) > 0:
			columns = ['id1', 'id2', 'text1', 'text2', 'similarity']
			if pair_text_i:
				columns += ['pair_of_text1', 'pair_of_text2', 'similarity_of_pair']
			similarity_df = pd.DataFrame(data=rows, columns=columns)
			output_file = f'_similarity_{check_col_name}.'.join(input_file.rsplit('.', 1))
			df_utils = DFUtils('df_utils')
			similarity_df.sort_values(by='similarity', ascending=False, inplace=True)
			df_utils.add_sid(similarity_df)
			df_utils.save(similarity_df, path, output_file, max_rows_in_file)
			print('{} [INFO][{}.save_similarity_df] Saved rows: {:,} in {}'.format(str(datetime.now()), app_name, len(similarity_df), output_file))
		else:
			print('{} [INFO][{}.save_similarity_df] No similar rows in {}'.format(str(datetime.now()), app_name, str(input_file)))


	def __init__(self, name, lang_codes=None, filters=None):
		self.name = name
		self.__lang_codes = lang_codes
		self.__filters = filters
