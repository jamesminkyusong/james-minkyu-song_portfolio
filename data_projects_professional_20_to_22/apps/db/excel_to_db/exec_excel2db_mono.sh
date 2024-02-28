#!/bin/bash

path=$1
input_file=$2
lang_col_n=$3
text_col_n=$4
project_id=$5
option=$6

if [ $option = "preview" ]; then
	./excel2db.py \
		-p $path \
		-i $input_file \
		--lang_col_ns $lang_col_n \
		--text_col_ns $text_col_n \
		--project_id $project_id \
		--preview
elif [ $option = "devel" ]; then
	./excel2db.py \
		-p $path \
		-i $input_file \
		--lang_col_ns $lang_col_n \
		--text_col_ns $text_col_n \
		--project_id $project_id
elif [ $option = "production" ]; then
	./excel2db.py \
		-p $path \
		-i $input_file \
		--lang_col_ns $lang_col_n \
		--text_col_ns $text_col_n \
		--project_id $project_id \
		--prod \
		-s
fi
