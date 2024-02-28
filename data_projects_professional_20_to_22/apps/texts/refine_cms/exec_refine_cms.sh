#!/bin/bash

input_file=$1

path=`echo ~/project/corpus_raw/texts/refine`

./refine_cms.py \
	-p $path \
	-i $input_file \
	--group_id_col_i 2 \
	--corpus_id_col_i 3 \
	--text_col_i 7 \
	--opcode_col_i 8 \
	--lang_col_i 9 \
	--new_lang_col_i 10 \
	--prod \
	-s
