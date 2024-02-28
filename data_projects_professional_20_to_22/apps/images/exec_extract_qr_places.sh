#!/bin/bash

lang=$1

path=`echo ~/project/corpus_raw/images/qr_places`
# output_file=`echo qr_places_ $lang.xlsx | sed 's/ //g'`
output_file=`echo qr_places_ $lang.csv | sed 's/ //g'`

./extract_qr_places.py \
	-p $path \
	-o $output_file \
	--lang $lang
