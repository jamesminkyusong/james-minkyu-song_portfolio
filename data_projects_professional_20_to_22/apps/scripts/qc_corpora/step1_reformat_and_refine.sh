#!/bin/bash

input_file=$1
lang1=$2
lang2=$3
col_i1=$4
col_i2=$5
output_file=`echo $input_file | sed -e 's/step0_/step1_/'`
path=`grep ^path config | head -1 | awk '{print $2}'`

echo ===== ===== =====
echo step1-1 reformat ...
echo ===== ===== =====

../../texts/manipulate_excel/manipulate_excel.py \
	-p $path/step0_source \
	-o $output_file \
	--add_sid \
	-i $input_file \
	--keep_all \
	--not_masking_piis \
	--col_indices $col_i1 $col_i2 \
	--col_names $lang1 $lang2

echo ===== ===== =====
echo step1-2 refine ...
echo ===== ===== =====

../../texts/check_quality/refine_corpus.py \
	-p $path/step0_source \
	-o $output_file \
	-i $output_file \
	--refine_col_is 2 3

mv $path/step0_source/step1*.xlsx $path/step1_refine
