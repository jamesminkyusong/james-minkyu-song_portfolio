#!/bin/bash

lang1=$1
lang2=$2

path=`echo ~/project/corpus_raw/texts/crowd_trs`
output_file=`echo crowd_trs_$lang1 _$lang2.csv | sed 's/ //g'`

echo ===== ===== =====
echo extract $lang1 and $lang2 crowd_trs ...
echo ===== ===== =====

./extract_crowd_trs.py \
	-p $path \
	-o $output_file \
	--lang1 $lang1 \
	--lang2 $lang2
