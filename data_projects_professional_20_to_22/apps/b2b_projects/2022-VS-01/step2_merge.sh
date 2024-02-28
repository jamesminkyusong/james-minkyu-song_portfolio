#!/bin/bash

yyyy=$1
mm=$2

path=`echo ~/project/corpus_raw/b2b_projects/2021/2021-VS-01/$yyyy$mm`

ls -al $path/news_eng*pass.xlsx | awk '{print $9}' | cut -d/ -f10 > $path/input_files_list1
ls -al $path/news_kor*pass.xlsx | awk '{print $9}' | cut -d/ -f10 > $path/input_files_list2
ls -al $path/user_contents*pass.xlsx | awk '{print $9}' | cut -d/ -f10 > $path/input_files_list3
ls -al $path/waiker_contents*pass.xlsx | awk '{print $9}' | cut -d/ -f10 > $path/input_files_list4

for i in `seq 1 4`; do
	input_files_list=`echo input_files_list$i`

	echo ===== ===== =====
	echo merge $i ...
	echo ===== ===== =====
	
	../../texts/refine_texts/check_dups.py \
		-p $path \
		--input_files_list $input_files_list \
		--check_col_ns sentence \
		--lang_penalty \
		--save_files unique
done
