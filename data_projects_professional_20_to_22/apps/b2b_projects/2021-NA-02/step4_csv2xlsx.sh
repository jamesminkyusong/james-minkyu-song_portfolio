#!/bin/bash

input_files_list=$1

path=`echo ~/project/corpus_raw/b2b_projects/2021/2021-NA-02`

while read line; do
	output_file=`echo $line | sed 's/step3/step4/' | sed 's/csv/xlsx/'`
	
	echo ===== ===== =====
	echo convert $line to $output_file ...
	echo ===== ===== =====

	../../texts/manipulate_excel/manipulate_excel.py \
		-p $path \
		-o $output_file \
		-i $line
done < $path/$input_files_list
