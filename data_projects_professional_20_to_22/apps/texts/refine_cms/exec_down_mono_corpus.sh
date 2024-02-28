#!/bin/bash

lang=$1

path=`echo ~/project/corpus_raw/texts/multi_pairs`
output_file=`echo corpus_$lang.csv`

echo ===== ===== =====
echo downloading $lang corpus ...
echo ===== ===== =====

./down_mono_corpus.py \
	-p $path \
	-o $output_file \
	--lang $lang \
	--prod
