#!/bin/bash

lang1=$1
lang2=$2

path=`echo /Volumes/Seagate/data/texts/2pair_corpus`
output_file=`echo stat_2pair_$lang1 2$lang2.xlsx | sed 's/ //g'`

./count_coprus.py \
	-p $path \
	-o $output_file \
	--langs $lang1 $lang2 \
	--tag_col_n new_tag
