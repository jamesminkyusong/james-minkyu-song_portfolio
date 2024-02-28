#!/bin/bash

env=$1
lang=$2
input_file=`echo mono_$lang _tag_ids.xlsx | sed -e 's/ //g'`
path=`echo ~/project/corpus_raw/texts/mono`

echo ===== ===== =====
echo step3 update tags on DB and ES ...
echo ===== ===== =====

if [[ $env == "prod" ]]; then
	echo prod: $input_file
	time ../../texts/refine_cms/update_corpus.py \
		-i $path/$input_file \
		--opcode_col_i 8 \
		--group_id_col_i 2 \
		--tag_id_col_i 7 \
		--prod \
		-s
else
	time ../../texts/refine_cms/update_corpus.py \
		-i $path/$input_file \
		--opcode_col_i 8 \
		--group_id_col_i 2 \
		--tag_id_col_i 7
fi
