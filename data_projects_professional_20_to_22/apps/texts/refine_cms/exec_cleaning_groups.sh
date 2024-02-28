#!/bin/bash

lang_code=$1

dup_file=`echo dup_mono_$lang_code.xlsx`
corpus_id_x=`echo $lang_code _id_x | sed -e 's/ //g'`
corpus_id_y=`echo $lang_code _id_y | sed -e 's/ //g'`

echo ===== ===== =====
echo merging same groups for $lang_code ...
echo ===== ===== =====
./merge_groups.py -p \
	~/project/corpus_raw/texts/mono \
	--dup_file $dup_file \
	--col_indices 0 1 2 3 4 \
	--col_names group_id_x $corpus_id_x $lang_code group_id_y $corpus_id_y \
	--update_db \
	--prod \
	-s
