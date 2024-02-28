#!/bin/bash

input_file=$1
src_lang=$2
dst_lang=$3
text_col_n=$4

path=`echo ~/project/corpus_raw/test`

./translate_textra.py \
	-p $path \
	-i $input_file \
	--src_lang $src_lang \
	--dst_lang $dst_lang \
	--text_col_n $text_col_n \
	--save_interval 100 \
	--prod \
	-s
