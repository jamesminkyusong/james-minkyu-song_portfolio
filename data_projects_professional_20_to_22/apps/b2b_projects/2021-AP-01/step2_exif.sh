#!/bin/bash

sub_path=$1

path=`echo ~/project/corpus_raw/b2b_projects/2021/2021-AP-01/$sub_path`

echo ===== ===== =====
echo extract exif ...
echo ===== ===== =====

./extract_exif.py \
	-p $path
