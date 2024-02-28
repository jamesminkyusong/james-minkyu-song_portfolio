#!/bin/bash

path=$1
input_file=$2
text_col_n=$3

./find_corpus.py \
	-p $path \
	-i $input_file \
	--text_col_n $text_col_n \
	--prod \
	-s
