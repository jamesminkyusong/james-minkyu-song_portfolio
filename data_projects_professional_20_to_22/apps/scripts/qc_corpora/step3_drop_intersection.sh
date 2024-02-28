#!/bin/bash

input_file=$1
lang1=$2
lang2=$3
input_file_in_F1=`echo $lang1 _$lang2 _1.xlsx | sed -e 's/ //g'`
input_file_in_F2=`echo $lang1 _$lang2 _2.xlsx | sed -e 's/ //g'`
output_file=`echo $input_file | sed -e 's/step2_/step3_/'`
output_file_dup_in_F=`echo $output_file | cut -d. -f1`
output_file_dup_in_F=`echo $output_file_dup_in_F _dup_in_F.xlsx | sed -e 's/ //g'`
path=`grep ^path config | head -1 | awk '{print $2}'`

echo ===== ===== =====
echo step3 copy $lang1 $lang2 corpora ...
echo ===== ===== =====

files=`echo $lang1 _$lang2*.xlsx | sed -e 's/ //g'`
cp ~/project/corpus_raw/texts/2pairs/$files $path/step2_drop_dup

echo ===== ===== =====
echo step3 find intersection ...
echo ===== ===== =====

../../texts/manipulate_excel/manipulate_excel.py \
	-p $path/step2_drop_dup \
	-o $output_file_dup_in_F \
	-i $input_file $input_file_in_F1 $input_file_in_F2 \
	--not_masking_piis \
	--col_names sid $lang1 $lang2 \
	--check_col_name $lang1 \
	--leave_intersection

echo ===== ===== =====
echo step3 drop intersection ...
echo ===== ===== =====

../../texts/manipulate_excel/manipulate_excel.py \
	-p $path/step2_drop_dup \
	-o $output_file \
	-i $input_file $input_file_in_F1 $input_file_in_F2 \
	--not_masking_piis \
	--col_names sid $lang1 $lang2 \
	--check_col_name $lang1 \
	--drop_intersection

rm $path/step2_drop_dup/$files
mv $path/step2_drop_dup/step3*.xlsx $path/step3_drop_intersection
