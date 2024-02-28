#!/bin/bash

input_file=$1
group_id_col_n=$2
option=$3

path=`echo ~/project/corpus_raw/texts/multi_pairs`

if [ $option = "preview" ]; then
	./excel2db.py \
		-p $path \
		-i $input_file \
		--group_id_col_n $group_id_col_n \
		--tag_name_col_ns topic_1 topic_2 topic_3 \
		--tag_score_col_ns score_1 score_2 score_3 \
		--preview
elif [ $option = "devel" ]; then
	./excel2db.py \
		-p $path \
		-i $input_file \
		--group_id_col_n $group_id_col_n \
		--tag_name_col_ns topic_1 topic_2 topic_3 \
		--tag_score_col_ns score_1 score_2 score_3
elif [ $option = "production" ]; then
	./excel2db.py \
		-p $path \
		-i $input_file \
		--group_id_col_n $group_id_col_n \
		--tag_name_col_ns topic_1 topic_2 topic_3 \
		--tag_score_col_ns score_1 score_2 score_3 \
		--prod \
		-s
fi
