#!/bin/bash

lang=$1

path=`echo ~/project/corpus_raw/texts/multi_pairs`
output_file=`echo $lang _refined.xlsx | sed 's/ //g'`
wrong_file=`echo $lang _wrong.csv | sed 's/ //g'`

../../texts/manipulate_excel/manipulate_excel.py \
	-p $path \
	-o $output_file \
	--add_sid \
	-i $wrong_file
