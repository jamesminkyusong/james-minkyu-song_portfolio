#!/bin/bash

input_files_list=$1
lang1=$1
lang2=$2

echo ===== ===== =====
echo check quality ...
echo ===== ===== =====

path=`echo ~/project/corpus_raw/b2b_projects/2021/2021-NA-02`
output_file=`echo $lang1 $lang2 _final.csv | sed 's/ //g'`

../../texts/check_quality/check_quality.py \
	-p $path \
	-o $output_file \
	--input_files_list $input_files_list \
	--add_filter_result \
	--not_check_in_flitto \
	--not_check_one_text \
	--not_check_similarity \
	--not_check_verb \
	--drop_if_email \
	--drop_if_tel \
	--drop_if_url
