import io
import math
import json
import pandas as pd
import streamlit as st


buf = io.BytesIO()
langs = {}
default_lang = 'Select'
all_lang = 'All'

lang_name2code_f = lambda lang_name: [lang['code'] for lang in langs if lang['name'] == lang_name][0]


def get_conf(file_p):
	conf = {}

	with open(file_p) as f:
		json_text = json.load(open(file_p))
		for key in json_text.keys():
			conf[key] = json_text[key]

	return conf


def read_stat_file(file_p):
	df = pd.read_excel(file_p)
	df['count'] = df['count'].apply(lambda x: math.trunc(x * 0.9))
	df = df[df['count'] > 0]

	return df


def get_lang_selectbox(name, langs):
	return st.selectbox(
		f'Please select {name} :',
		[lang['name'] for lang in langs]
	)


def process_all2all_stat(df):
	stat_df = df.sort_values(by=['lang1', 'lang2', 'tag'])
	st.write(stat_df)
	st.info('All : {:,} sentences'.format(df['count'].sum()))

	save_df_as_xlsx(stat_df)
	down_file(f'stat_all.xlsx')


def process_one2all_stat(df, lang_name):
	lang_code = lang_name2code_f(lang_name)
	stat_df = df[df['lang1_code'] == lang_code]
	stat_df2 = df[df['lang2_code'] == lang_code][['lang2', 'lang1', 'tag', 'count', 'lang2_code', 'lang1_code']]
	stat_df2.rename(columns={'lang1': 'lang2', 'lang2': 'lang1', 'lang1_code': 'lang2_code', 'lang2_code': 'lang1_code'}, inplace=True)
	stat_df = pd.concat([stat_df, stat_df2])
	stat_df.sort_values(by=['lang2', 'tag'], inplace=True)
	st.write(stat_df)
	st.info('All : {:,} sentences'.format(stat_df['count'].sum()))

	save_df_as_xlsx(stat_df)
	down_file(f'stat_{lang_code}.xlsx')


def process_one2one_stat(df, lang1_name, lang2_name):
	lang1_code = lang_name2code_f(lang1_name)
	lang2_code = lang_name2code_f(lang2_name)
	stat_df = df[((df['lang1_code'] == lang1_code) & (df['lang2_code'] == lang2_code)) | ((df['lang1_code'] == lang2_code) & (df['lang2_code'] == lang1_code))]
	stat_df = stat_df.assign(lang1=lang1_name, lang2=lang2_name, lang1_code=lang1_code, lang2_code=lang2_code)
	st.write(stat_df)
	st.info('All : {:,} sentences'.format(stat_df['count'].sum()))

	save_df_as_xlsx(stat_df)
	down_file(f'stat_{lang1_code}2{lang2_code}.xlsx')


def save_df_as_xlsx(df):
	with pd.ExcelWriter(buf, engine='xlsxwriter') as writer:
		df.to_excel(writer, index=False)
		writer.save()


def down_file(filename):
	st.download_button(
		label='Click HERE to download!',
		data=buf,
		file_name=filename
	)


def main():
	st.title('Corpus Stat')

	conf = get_conf('config.json')

	global langs
	langs = conf['langs']

	df = read_stat_file(conf['stat_file_p'])

	lang1_option = get_lang_selectbox('lang1', langs)
	lang2_option = get_lang_selectbox('lang2', langs)

	if lang1_option != default_lang and lang2_option != default_lang:
		if lang1_option != all_lang and lang1_option == lang2_option:
			st.write(f'You should select TWO different languages!')
		elif lang1_option == all_lang and lang2_option == all_lang:
			process_all2all_stat(df)
		elif lang2_option == all_lang:
			process_one2all_stat(df, lang1_option)
		elif lang1_option == all_lang:
			process_one2all_stat(df, lang2_option)
		else:
			process_one2one_stat(df, lang1_option, lang2_option)


if __name__ == '__main__':
	main()
