#!/bin/bash

lang=$1

path=`echo ~/project/corpus_raw/texts/multi_pairs`

input_file=`echo $lang _not_classified.xlsx | sed 's/ //g'`

../../texts/classifier/topic_classifier.py \
	-p $path \
	-i $input_file \
	--lang $lang \
	--text_col_n $lang
