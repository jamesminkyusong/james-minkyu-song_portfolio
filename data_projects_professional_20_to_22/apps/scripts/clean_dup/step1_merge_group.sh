#!/bin/bash

lang=$1
last_file_i=$2

path=`echo ~/project/corpus_raw/texts/mono`
output_file=`echo dup_mono_$lang.xlsx`

echo ===== ===== =====
echo merge groups for $lang ...
echo ===== ===== =====

cat /dev/null > $path/input_files_list
for i in `seq 1 $last_file_i`; do
	echo mono_$lang _$i.xlsx | sed 's/ //g' >> $path/input_files_list
done

corpus_id=`echo $lang _id | sed 's/ //g'`
corpus_id_x=`echo $lang _id_x | sed 's/ //g'`
corpus_id_y=`echo $lang _id_y | sed 's/ //g'`

../../texts/refine_cms/merge_groups.py \
	-p $path \
	-o $output_file \
	--input_files_list input_files_list \
	--lang_code $lang \
	--col_indices 1 2 3
