#!/bin/bash

path=`echo /Volumes/Seagate/data/texts/2pair_corpus`
output_file=`echo stat_2pair.xlsx`

./count_corpus.py \
	-p $path \
	-o $output_file \
	--tag_col_n new_tag \
	--2pair
