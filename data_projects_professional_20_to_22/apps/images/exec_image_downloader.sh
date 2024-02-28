#!/bin/bash

input_file=$1
count=$2

path=`echo ~/project/corpus_raw/images/qr_places`

./image_downloader.py \
	-p $path \
	-c $count \
	-i $input_file \
	--address_col_n address \
	--url_col_n image_url
