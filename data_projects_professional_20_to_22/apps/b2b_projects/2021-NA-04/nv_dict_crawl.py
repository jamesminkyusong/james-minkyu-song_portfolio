#!../../../bin/python3

import os
from selenium import webdriver
import pandas as pd
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def replace_chars(sentence):
	replaced_s = sentence
	for useless_char in ["?", "%"]:
		replaced_s = replaced_s.replace(useless_char, "")
	return replaced_s


def open_close_driver(n, driver, driver_path):
	if n % 100 == 0 & n != 0:  # restarts the driver every 100 lines.
		driver.quit()
		time.sleep(1)
		driver = webdriver.Chrome(driver_path)

	return driver


def selenium_nv_dict(driver, text):
	return_bool = "FALSE"

	query_text = replace_chars(text)
	low_trimmed_text = (" ").join(query_text.split()).lower()

	url = "https://en.dict.naver.com/#/search?range=example&shouldSearchVlive=false&query="
	query = ("%20").join(query_text.split())

	final_url = url + query
	driver.get(final_url)
	# time.sleep(0.5)
	try:
		element = WebDriverWait(driver, 5).until(
			EC.presence_of_element_located((By.CLASS_NAME, "text"))
		)
	except:
		return_bool = "LOAD_ERROR"
		return return_bool
	examples = driver.find_elements_by_class_name("text")

	for e in examples:
		sentence = e.text
		to_compare_res = replace_chars(sentence)
		low_res_sentence = (" ").join(to_compare_res.split()).lower()
		if low_res_sentence == low_trimmed_text:
			return_bool = "TRUE"
			return return_bool
		# print(return_bool)

	# driver.quit()
	return return_bool


def save_intervals(
	filename, work_df, split_count, found_list, ppg_found_list, source_list
):
	temp_list = found_list.copy()
	temp_ppg = ppg_found_list.copy()
	temp_src = source_list.copy()
	for i in range(0, len(df) - len(temp_list)):
		temp_list.append("")
		temp_ppg.append("")
		temp_src.append("")
	work_df["dict_example_check"] = temp_list
	work_df["ppg?"] = temp_ppg
	work_df["source?"] = temp_src
	part_name = str(split_count) + "_" + filename
	work_df.to_excel(os.path.join(out_path, part_name), index=None)
	print(part_name)
	split_count += 1

	return work_df, split_count


def check_ppg(driver, text):
	return_bool = "FALSE"
	source = ""
	query_text = replace_chars(text)
	low_trimmed_text = (" ").join(query_text.split()).lower()

	url = "https://en.dict.naver.com/#/search?range=example&shouldSearchVlive=false&query="
	query = ("%20").join(query_text.split())

	final_url = url + query
	driver.get(final_url)

	try:
		element = WebDriverWait(driver, 3).until(
			EC.presence_of_element_located((By.CLASS_NAME, "text"))
		)
	except:
		return_bool = "LOAD_ERROR"
		return return_bool, return_bool

	rows = driver.find_elements_by_class_name("row")
	for r in rows:
		ppg = []
		example = r.find_elements_by_class_name("text")
		btns = r.find_elements_by_tag_name("button")
		ppg = [b.text for b in btns]
		sentence = example[0].text
		try:
			src = r.find_element_by_class_name("source")
			source = src.text
		except:
			pass
		to_compare_res = replace_chars(sentence)
		low_res_sentence = (" ").join(to_compare_res.split()).lower()
		if low_res_sentence == low_trimmed_text and "Papago Translate" in ppg:
			return_bool = "TRUE"
			return return_bool, source
	return return_bool, source


def check_nv_dict_ppg(driver, text):
	return_found = "FALSE"
	return_ppg = "FALSE"
	source = ""

	query_text = replace_chars(text)
	low_trimmed_text = (" ").join(query_text.split()).lower()

	url = "https://en.dict.naver.com/#/search?range=example&shouldSearchVlive=false&query="
	query = ("%20").join(query_text.split())

	final_url = url + query
	driver.get(final_url)

	try:
		element = WebDriverWait(driver, 3).until(
			EC.presence_of_element_located((By.CLASS_NAME, "text"))
		)
	except:
		return_found = "LOAD_ERROR"
		return return_found, return_found, return_found  # all load error

	rows = driver.find_elements_by_class_name("row")  # pull out each sentence box
	for r in rows:
		ppg = []
		example = r.find_elements_by_class_name("text")
		btns = r.find_elements_by_tag_name("button")
		ppg = [b.text for b in btns]  # many buttons
		sentence = example[0].text  # only en
		try:
			src = r.find_element_by_class_name("source")
			source = src.text
		except:
			pass
		to_compare_res = replace_chars(sentence)
		low_res_sentence = (" ").join(to_compare_res.split()).lower()
		if low_res_sentence == low_trimmed_text:
			return_found = "TRUE"
			if "Papago Translate" in ppg:
				return_ppg = "TRUE"
			else:
				pass
			return return_found, return_ppg, source
		else:
			source = ""

	return return_found, return_ppg, source


if __name__ == "__main__":
	in_path = '/home/ubuntu/project/corpus_raw/b2b_projects/2021/2021-NA-04/result'
	out_path = '/home/ubuntu/project/corpus_raw/b2b_projects/2021/2021-NA-04/result/result'
	driver_path = '/home/ubuntu/bin/chromedriver'
	for f in sorted(os.listdir(in_path)):
		parts = 1
		print(f)

		if f.startswith(".") or f.startswith("~"):
			continue

		df = pd.read_excel(os.path.join(in_path, f))
		en_to_check = df["en"].values.tolist()

		result_list = []
		ppg_list = []
		src_list = []

		cdriver = webdriver.Chrome(driver_path)

		for n, t in enumerate(en_to_check):
			cdriver = open_close_driver(n, cdriver, driver_path)

			result, ppg_result, t_src = check_nv_dict_ppg(cdriver, t)
			result_list.append(result)
			ppg_list.append(ppg_result)
			src_list.append(t_src)

			if len(result_list) % (len(df) // 5) == 0 & len(result_list) != len(df):
				df, parts = save_intervals(
					f, df, parts, result_list, ppg_list, src_list
				)
		df["dict_example_check"] = result_list
		df["ppg?"] = ppg_list
		df["source?"] = src_list

		print(f)
		df.to_excel(os.path.join(out_path, ("dbl_chkd_" + f)), index=None)
		try:
			cdriver.quit()
		except:
			pass
