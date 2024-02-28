#!/bin/bash

input_file=$1
lang1=$2
lang2=$3
path=`grep ^path config | head -1 | awk '{print $2}'`

echo ===== ===== =====
echo [1/3] step2 drop empty for $lang1 ...
echo ===== ===== =====

output_file=`echo $input_file | sed -e 's/step1_/step2_/' | cut -d. -f1`
output_file=`echo $output_file _empty_$lang1.xlsx | sed -e 's/ //g'`
../../texts/manipulate_excel/manipulate_excel.py \
	-p $path/step1_refine \
	-o $output_file \
	-i $input_file \
	--not_masking_piis \
	--col_names sid $lang1 $lang2 \
	--check_col_name $lang1 \
	--drop_not_empty \
	--keep_all

echo ===== ===== =====
echo [2/3] step2 drop empty for $lang2 ...
echo ===== ===== =====

output_file=`echo $input_file | sed -e 's/step1_/step2_/' | cut -d. -f1`
output_file=`echo $output_file _empty_$lang2.xlsx | sed -e 's/ //g'`
../../texts/manipulate_excel/manipulate_excel.py \
	-p $path/step1_refine \
	-o $output_file \
	-i $input_file \
	--not_masking_piis \
	--col_names sid $lang1 $lang2 \
	--check_col_name $lang2 \
	--drop_not_empty \
	--keep_all

echo ===== ===== =====
echo [3/3] step2 drop dup ...
echo ===== ===== =====

output_file=`echo $input_file | sed -e 's/step1_/step2_/'`
../../texts/manipulate_excel/manipulate_excel.py \
	-p $path/step1_refine \
	-o $output_file \
	-i $input_file \
	--not_masking_piis \
	--col_names sid $lang1 $lang2 \
	--check_col_name $lang1 \
	--drop_empty \
	--keep_all

../../texts/manipulate_excel/manipulate_excel.py \
	-p $path/step1_refine \
	-o $output_file \
	-i $output_file \
	--not_masking_piis \
	--col_names sid $lang1 $lang2 \
	--check_col_name $lang2 \
	--drop_empty \
	--keep_all

../../texts/manipulate_excel/manipulate_excel.py \
	-p $path/step1_refine \
	-o $output_file \
	--save_dup \
	-i $output_file \
	--not_masking_piis \
	--col_names sid $lang1 $lang2

mv $path/step1_refine/step2*.xlsx $path/step2_drop_empty_and_dup
