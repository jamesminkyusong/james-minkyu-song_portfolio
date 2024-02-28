#!/bin/bash

lang=$1
input_file=$2

path=`echo ~/project/corpus_raw/texts/multi_pairs`
lang_id=`echo $lang _id | sed 's/ //g'`

../../db/merge_groups/merge_groups.py \
	-p $path \
	-i $input_file \
	--group_id_col_n group_id \
	--corpus_id_col_n $lang_id \
	--group_sid_col_n group_sid \
	--not_test \
	--prod \
	-s
