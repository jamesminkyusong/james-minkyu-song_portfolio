#!/bin/bash

echo ===== ===== =====
echo extracting all ...
echo ===== ===== =====

path=`echo ~/project/corpus_raw/texts/mono`
output_file=`echo corpus_raw.xlsx`

./db_to_excel.py \
	-p $path \
	-o $output_file \
	--corpus_raw \
	--ignore_not_in_group \
	--prod \
	-s
