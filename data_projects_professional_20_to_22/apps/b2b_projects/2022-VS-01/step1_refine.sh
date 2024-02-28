#!/bin/bash

yyyy=$1
mm=$2

path=`echo ~/project/corpus_raw/b2b_projects/2021/2021-VS-01/$yyyy$mm`

ls -al $path/*.xlsx | awk '{print $9}' | cut -d/ -f10 > $path/input_files_list
all_count=`wc -l $path/input_files_list | awk '{print $1}'`
(( i=0 ))

while read line; do
	(( i=i+1 ))
	echo ===== ===== =====
	echo $i of $all_count : refine $line ...
	echo ===== ===== =====

	if [ `echo $line | grep eng | wc -l | awk '{print $1}'` -eq 1 ]; then
		lang=`echo en`
	else
		lang=`echo ko`
	fi

	../../texts/refine_texts/refine_texts.py \
		-p $path \
		-i $line \
		--langs $lang \
		--text_col_ns sentence \
		--min_words_count 3 \
		--max_words_count 100
done < $path/input_files_list
