#!/bin/bash

input_file=$1
option=$2

(( project_id=65 ))
(( text_col_i=1 ))
(( lang_col_i=2 ))

path=`echo ~/project/corpus_raw/texts/multi_pairs`

if [ $option = "preview" ]; then
	../../db/excel_to_db/excel_to_db.py \
		-p $path \
		-i $input_file \
		--col_indices $text_col_i $lang_col_i \
		--col_names text lang \
		--lang_col_names lang \
		--text_col_names text \
		--project_id $project_id \
		--preview
elif [ $option = "devel" ]; then
	../../db/excel_to_db/excel_to_db.py \
		-p $path \
		-i $input_file \
		--col_indices $text_col_i $lang_col_i \
		--col_names text lang \
		--lang_col_names lang \
		--text_col_names text \
		--project_id $project_id
elif [ $option = "production" ]; then
	../../db/excel_to_db/excel_to_db.py \
		-p $path \
		-i $input_file \
		--col_indices $text_col_i $lang_col_i \
		--col_names text lang \
		--lang_col_names lang \
		--text_col_names text \
		--project_id $project_id \
		--prod \
		-s
fi
