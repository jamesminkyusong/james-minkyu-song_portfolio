#!/bin/bash

sub_path=$1
drive_id=$2

path=`echo ~/project/corpus_raw/b2b_projects/2021/2021-AP-01/$sub_path`

echo ===== ===== =====
echo download heic files ...
echo ===== ===== =====

./down_heic.py \
	-p $path \
	--drive_id $drive_id
