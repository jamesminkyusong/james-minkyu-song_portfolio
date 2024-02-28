#!/bin/bash

path=$1
input_file=$2
lang_col_n1=$3
lang_col_n2=$4
text_col_n1=$5
text_col_n2=$6
project_id=$7
option=$8

if [ $option = "preview" ]; then
	./excel2db.py \
		-p $path \
		-i $input_file \
		--lang_col_ns $lang_col_n1 $lang_col_n2 \
		--text_col_ns $text_col_n1 $text_col_n2 \
		--project_id $project_id \
		--preview
elif [ $option = "devel" ]; then
	./excel2db.py \
		-p $path \
		-i $input_file \
		--lang_col_ns $lang_col_n1 $lang_col_n2 \
		--text_col_ns $text_col_n1 $text_col_n2 \
		--project_id $project_id
elif [ $option = "production" ]; then
	./excel2db.py \
		-p $path \
		-i $input_file \
		--lang_col_ns $lang_col_n1 $lang_col_n2 \
		--text_col_ns $text_col_n1 $text_col_n2 \
		--project_id $project_id \
		--prod \
		-s
fi
