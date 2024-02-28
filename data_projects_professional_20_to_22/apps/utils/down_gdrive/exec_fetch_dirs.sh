#!/bin/bash

path=$1
drive_id=$2

output_file=`echo sub_dirs.xlsx`
mkdir -p $path

./down_gdrive.py \
	-p $path \
	-o $output_file \
	--drive_id $drive_id \
	--sub_dirs
