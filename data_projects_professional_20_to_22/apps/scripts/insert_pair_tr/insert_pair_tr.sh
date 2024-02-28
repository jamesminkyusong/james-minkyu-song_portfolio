#!/bin/bash

input_file=$1
option=$2
lang1=$3
lang2=$4

path=`echo ~/project/corpus_raw/texts/arcade/tred_by_linguists`

if [ $option = "preview" ]; then
	../../db/excel_to_db/excel_to_db.py \
		-p $path \
		-i $input_file \
		--col_indices 3 4 \
		--col_names $lang1 $lang2 \
		--preview
elif [ $option = "development" ]; then
	../../db/excel_to_db/excel_to_db.py \
		-p $path \
		-i $input_file \
		--col_indices 3 4 \
		--col_names $lang1 $lang2
elif [ $option = "production" ]; then
	../../db/excel_to_db/excel_to_db.py \
		-p $path \
		-i $input_file \
		--col_indices 3 4 \
		--col_names $lang1 $lang2 \
		--prod \
		-s
fi
