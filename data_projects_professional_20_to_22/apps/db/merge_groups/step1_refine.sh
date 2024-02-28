#!/bin/bash

lang=$1
input_file=$2

path=`echo ~/project/corpus_raw/texts/multi_pairs`

../../texts/refine_texts/refine_texts.py \
	-p $path \
	-i $input_file \
	--langs $lang \
	--text_col_ns $lang \
	--not_apply_filters

# delete *_refined.xlsx
# rename *_result.xlsx -> *_refine.xlsx
