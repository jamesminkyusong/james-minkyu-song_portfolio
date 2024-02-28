#!/bin/bash

lang1=$1
lang2=$2
lang3=$3
lang4=$4
lang5=$5

langs=`echo $lang1 $lang2 $lang3 $lang4 $lang5`
path=`echo ~/project/corpus_raw/texts/multi_pairs`
output_file=`echo $langs.xlsx | sed 's/ //g'`

echo ===== ===== =====
echo extract $langs ...
echo ===== ===== =====

./db_to_excel.py \
	-p $path \
	-o $output_file \
	-m 100000 \
	--lang_codes $langs \
	--add_ids \
	--add_delivery \
	--add_tag \
	--prod \
	-s
