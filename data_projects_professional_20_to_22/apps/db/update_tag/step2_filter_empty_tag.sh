#!/bin/bash

lang=$1
end_i=$2

path=`echo ~/project/corpus_raw/texts/multi_pairs`

for i in `seq 1 $end_i`; do
	input_file=`echo $lang _$i.xlsx | sed 's/ //g'`

	echo ===== ===== =====
	echo $i of $end_i : search sentences, which are not classified, in $input_file ...
	echo ===== ===== =====

	../../texts/refine_texts/search_words.py \
		-p $path \
		-i $input_file \
		--check_col_ns tag \
		--search_empty \
		--save_files found
done
