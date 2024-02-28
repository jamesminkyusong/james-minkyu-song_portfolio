#!/bin/bash

lang_code=$1

input_files_list=`echo mono_$lang_code _list | sed -e 's/ //g'`
dup_file=`echo dup_mono_$lang_code.xlsx`
corpus_id=`echo $lang_code _id | sed -e 's/ //g'`
corpus_id_x=`echo $lang_code _id_x | sed -e 's/ //g'`
corpus_id_y=`echo $lang_code _id_y | sed -e 's/ //g'`

echo ===== ===== =====
echo searching same groups for $lang_code ...
echo ===== ===== =====
./merge_groups.py \
	-p ~/project/corpus_raw/texts/mono \
	-o $dup_file \
	--input_files_list $input_files_list \
	--col_indices 1 2 3 \
	--col_names group_id $corpus_id $lang_code \
	-s
