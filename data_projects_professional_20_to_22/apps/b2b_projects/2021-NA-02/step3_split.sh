#!/bin/bash

input_files_list=$1
lang1=$1
lang2=$2

echo ===== ===== =====
echo split ...
echo ===== ===== =====

path=`echo ~/project/corpus_raw/b2b_projects/2021/2021-NA-02`
output_file=`echo step3_ $lang1 2$lang2.csv | sed 's/ //g'`

../../texts/manipulate_excel/manipulate_excel.py \
	-p $path \
	-o $output_file \
	--input_files_list $input_files_list \
	--split \
	--check_col_name tag
