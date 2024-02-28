#!/bin/bash

path=$1
input_file=$2
corpus_id_col_n=$3

./find_corpus.py \
	-p $path \
	-i $input_file \
	--corpus_id_col_n $corpus_id_col_n \
	--prod \
	-s
