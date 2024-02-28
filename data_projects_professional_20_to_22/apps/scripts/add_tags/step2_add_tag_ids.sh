#!/bin/bash

lang=$1
input_file=`echo mono_$lang _tags.xlsx | sed -e 's/ //g'`
lang_id_name=`echo $lang _id | sed -e 's/ //g'`
lang_source=`echo $lang _source | sed -e 's/ //g'`
input_files_list=`echo mono_$lang _list_tags | sed -e 's/ //g'`
path=`echo ~/project/corpus_raw/texts/mono`

echo ===== ===== =====
echo step2-1 adding tag ids ...
echo ===== ===== =====

cat /dev/null > $path/$input_files_list

while read line; do
	tag_ko=`echo $line | awk '{print $1}'`
	tag_en=`echo $line | awk '{print $2}'`
	tag_id=`echo $line | awk '{print $3}'`
	output_file=`echo mono_$lang _$tag_en.xlsx | sed -e 's/ //g'`
	echo $output_file >> $path/$input_files_list

	../../texts/manipulate_excel/manipulate_excel.py \
		-p $path \
		-o $output_file \
		--add_sid \
		-i $input_file \
		--keep_all \
		--not_masking_piis \
		--col_indices 1 2 3 4 5 \
		--col_names group_id $lang_id_name $lang $lang_source tag \
		--check_col_name tag \
		--leave_keywords $tag_ko \
		--start_with_keyword \
		--add_col_name tag_id \
		--add_col_value $tag_id
done < ./tags_list

echo ===== ===== =====
echo step2-2 adding opcode ...
echo ===== ===== =====

output_file=`echo mono_$lang _tag_ids.xlsx | sed -e 's/ //g'`
../../texts/manipulate_excel/manipulate_excel.py \
	-p $path \
	-o $output_file \
	--add_sid \
	--input_files_list $input_files_list \
	--keep_all \
	--not_masking_piis \
	--col_indices 1 2 3 4 5 6 \
	--col_names group_id $lang_id_name $lang $lang_source tag tag_id \
	--add_col_name opcode \
	--add_col_value U_D
