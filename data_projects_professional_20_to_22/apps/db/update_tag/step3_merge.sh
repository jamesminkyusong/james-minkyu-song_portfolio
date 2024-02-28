#!/bin/bash

lang=$1

path=`echo ~/project/corpus_raw/texts/multi_pairs`

ls -al $path/$lang*result_found.xlsx | awk '{print $9}' | cut -d/ -f8 > $path/input_files_list

../../texts/manipulate_excel/manipulate_excel.py \
	-p $path \
	--add_sid \
	--input_files_list input_files_list \
	--sort_by group_id
