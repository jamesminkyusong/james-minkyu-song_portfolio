#!/bin/bash

input_files_list=$1
lang1=$2
lang2=$3

echo ===== ===== =====
echo drop dup ...
echo ===== ===== =====

path=`echo ~/project/corpus_raw/b2b_projects/2021/2021-NA-02`
output_file=`echo step1_$lang1 2$lang2.xlsx | sed 's/ //g'`

../../texts/manipulate_excel/manipulate_excel.py \
	-p $path \
	-o $output_file \
	--input_files_list $input_files_list \
	-i $input_file \
	--drop_dup \
	--check_col_names $lang1 $lang2 \
	--check_each_col
