#!/bin/bash

input_file=$1
lang1=$2
lang2=$3
output_file=`echo $input_file | sed -e 's/step3_/step4_/'`
path=`grep ^path config | head -1 | awk '{print $2}'`

echo ===== ===== =====
echo step4 check quality $input_file ...
echo ===== ===== =====

cp $path/step3_drop_intersection/$input_file $path/step4_check_quality/$output_file

../../texts/check_quality/check_quality.py \
	-p $path/step4_check_quality \
	-i $output_file \
	--col_names sid $lang1 $lang2 \
	--add_filter_result \
	--not_check_in_flitto \
	--not_check_one_text \
	--not_check_profanity \
	--not_masking_piis \
	--drop_url \
	--drop_email \
	--similarity_col_name $lang1 \
	--similarity_sid_col_name sid
