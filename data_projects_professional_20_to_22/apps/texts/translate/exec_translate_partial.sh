#!/bin/bash

input_file=$1
src_lang=$2
dst_lang=$3
text=$4
node_i=$5
all_nodes_count=$6

./translate_partial.py \
	-p ~/project/corpus_raw/test \
	-i $input_file \
	--src_lang $src_lang \
	--dst_lang $dst_lang \
	--text_col_n $text \
	--save_interval 1000 \
	--node_i $node_i \
	--all_nodes_count $all_nodes_count \
	--prod \
	-s
