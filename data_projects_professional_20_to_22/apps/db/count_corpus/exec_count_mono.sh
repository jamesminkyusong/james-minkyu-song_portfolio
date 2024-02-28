#!/bin/bash

path=`echo /Volumes/Seagate/data/texts/mono_corpus`
output_file=`echo stat_mono.xlsx`

./count_corpus.py \
	-p $path \
	-o $output_file \
	--tag_col_n new_tag \
	--mono
