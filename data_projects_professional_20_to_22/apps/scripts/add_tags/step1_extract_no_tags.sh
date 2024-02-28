#!/bin/bash

lang=$1
output_file=`echo mono_$lang _no_tags.xlsx | sed -e 's/ //g'`
input_files_list=`echo mono_$lang _list | sed -e 's/ //g'`
lang_id_name=`echo $lang _id | sed -e 's/ //g'`
lang_source=`echo $lang _source | sed -e 's/ //g'`
path=`echo ~/project/corpus_raw/texts/mono`

echo ===== ===== =====
echo step1 extract corpora which have not yet tagged ...
echo ===== ===== =====

../../texts/manipulate_excel/manipulate_excel.py \
	-p $path \
	-o $output_file \
	--add_sid \
	--input_files_list $input_files_list \
	--keep_all \
	--not_masking_piis \
	--col_indices 1 2 3 4 5 \
	--col_names group_id $lang_id_name $lang $lang_source tag \
	--check_col_name $lang \
	--drop_not_empty
