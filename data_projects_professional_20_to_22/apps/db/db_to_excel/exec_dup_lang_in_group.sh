#!/bin/bash

path=`echo ~/project/corpus_raw/texts/2pairs`
output_file=`echo dup_lang_in_group.xlsx`

./broken_integrities.py \
	-p $path \
	-o $output_file \
	--dup_lang_in_group \
	--prod \
	-s
