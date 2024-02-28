from datetime import datetime
import json
import os
import pandas as pd
import shutil
import streamlit as st
import textdistance
import zipfile


output_file_f = lambda orig_file, kind: f'_{kind}.'.join(orig_file.rsplit('.', 1)) if '.' in orig_file else orig_file + '_{kind}'
basename_f = lambda orig_file_p: orig_file_p.rsplit('/', 1)[-1] if '/' in orig_file_p else orig_file_p
filename_f = lambda orig_file: orig_file.rsplit('.', 1)[0] if '.' in orig_file else orig_file
extension_f = lambda orig_file: orig_file.rsplit('.', 1)[-1].lower() if '.' in orig_file else ''
similarity_f = textdistance.sorensen_dice.normalized_similarity


def get_config(file_p):
	config = {}

	with open(file_p) as f:
		config = json.load(open(file_p))

	return config


def calculate_similarities(texts1, texts2):
	return list(map(lambda x: similarity_f(str(x[0]).lower(), str(x[1]).lower()), zip(texts1, texts2)))


def process_by_threshold(df, data_root_path, orig_name, threshold):
	now_str = datetime.today().strftime('%Y%m%d%H%M%S')

	data_path = os.path.join(data_root_path, now_str)
	os.mkdir(data_path)

	if threshold == 0:
		output_files_p = save_files([df], ['sim'], data_path, orig_name)
		with open(output_files_p[0], 'rb') as f:
			down_file('Download XLSX', basename_f(output_files_p[0]), f)
	else:
		high_list = df['similarity'] >= threshold
		high_df = df[high_list]
		low_df = df[~high_list]
		output_files_p = save_files([high_df, low_df], ['sim_high', 'sim_low'], data_path, orig_name)

		zip_output_file_p = zip_files(data_root_path, data_path, orig_name, output_files_p)
		with open(zip_output_file_p, 'rb') as f:
			down_file(f'Download ZIP', basename_f(zip_output_file_p), f)


def save_files(dfs, kinds, data_path, orig_name):
	output_files_p = []

	for df, kind in zip(dfs, kinds):
		output_file_p = os.path.join(data_path, output_file_f(orig_name, kind))
		df.to_excel(output_file_p, index=False, engine='xlsxwriter')
		output_files_p += [output_file_p]

	return output_files_p


def zip_files(data_root_path, data_path, orig_name, output_files_p):
	zip_output_file_p = os.path.join(data_root_path, filename_f(orig_name))
	shutil.make_archive(zip_output_file_p, format='zip', root_dir=data_path)

	return zip_output_file_p + '.zip'


def down_file(button_name, filename, f):
	st.download_button(
		label=button_name,
		data=f,
		file_name=filename
	)


def main():
	config = get_config('config.json')
	data_root_path = config['data_root_path']
	threshold_list = config['threshold_list']

	st.title('Similarity Calculator')

	uploaded_file = st.file_uploader("Choose a XLSX file :")
	if uploaded_file:
		if extension_f(uploaded_file.name) == 'xlsx':
			df = pd.read_excel(uploaded_file)
			st.write(df)

			st.write('Choose TWO columns to calculate similarity :')
			col_ns_options = list(map(st.checkbox, df.columns))
			selected_col_ns = [df.columns[i] for i in [i for i, v in enumerate(col_ns_options) if v]]

			if len(selected_col_ns) == 2:
				threshold_option = st.selectbox('Threshold (0: Don\'t filter by threshold) :', threshold_list)
				if st.button('Click HERE to calculate similarity. It\'ll take a few minutes.'):
					df['similarity'] = calculate_similarities(df[selected_col_ns[0]], df[selected_col_ns[1]])
					process_by_threshold(df, data_root_path, uploaded_file.name, threshold_option)
			else:
				st.write('You should choose only TWO columns!')
		else:
			st.write('Not a XLSX file!')


if __name__ == '__main__':
	main()
