#!/bin/bash

lang=$1

path=`echo ~/project/corpus_raw/texts/multi_pairs`
output_file=`echo $lang _result.csv | sed 's/ //g'`

../../texts/refine_texts/check_dups.py \
	-p $path \
	-o $output_file \
	--input_files_list input_files_list \
	--check_col_ns $lang \
	--lang_penalty \
	--add_group_sid \
	--save_files all_dup

# rename all_dup.csv -> all_dup.xlsx
