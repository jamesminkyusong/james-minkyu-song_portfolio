#!/bin/bash

lang=$1

path=`echo ~/project/corpus_raw/texts/multi_pairs`
wrong_file=`echo $lang _wrong.csv | sed 's/ //g'`

while read input_file; do
	echo ===== ===== =====
	echo grep wrong characters in $input_file ...
	echo ===== ===== =====

	file_prefix=`echo $input_file | cut -d. -f1`
	output_file=`echo $file_prefix.csv`

	../../texts/manipulate_excel/manipulate_excel.py \
		-p $path \
		-o $output_file \
		-i $input_file

	grep '	' $path/$output_file >> $path/$wrong_file
	grep '' $path/$output_file >> $path/$wrong_file
	grep "$(printf %b '\u200b')" $path/$output_file >> $path/$wrong_file

	count=`wc -l $path/$wrong_file | awk '{print $1}'`
	echo total $count sentence\(s\) found!
done < $path/input_files_list
