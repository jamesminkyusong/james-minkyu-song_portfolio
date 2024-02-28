#!/bin/bash

lang1=$1
lang2=$2
lang3=$3

path=`echo ~/project/corpus_raw/speeches`

./categorize_stat.py \
	-p $path \
	--events_file valid_events_list \
	--langs $lang1 $lang2 $lang3
