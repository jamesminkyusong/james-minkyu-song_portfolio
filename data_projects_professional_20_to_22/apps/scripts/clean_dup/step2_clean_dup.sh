#!/bin/bash

lang=$1

path=`echo ~/project/corpus_raw/texts/mono`
input_file=`echo dup_mono_$lang.xlsx`
corpus_id_x=`echo $lang_code _id_x | sed -e 's/ //g'`
corpus_id_y=`echo $lang_code _id_y | sed -e 's/ //g'`

echo ===== ===== =====
echo clean dup for $lang ...
echo ===== ===== =====

../../texts/refine_cms/merge_groups.py \
	-p $path \
	--dup_file $input_file \
	--lang_code $lang \
	--update_db \
	--prod \
	-s
