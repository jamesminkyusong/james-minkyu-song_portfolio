#!/bin/bash

all_count=`wc -l ./input_files_list | awk '{print $1}'`
(( index=0 ))

while read line; do
	filename=`echo $line | cut -d, -f1`

	(( index=index+1 ))
	echo [$index/$all_count] Preview $filename

	is_comment=`echo $line | grep '^#' | wc -l | awk '{print $1}'`
	if [ $is_comment -eq 1 ]; then
		echo $filename will be ignored.
	else
		./preview_excel.py -i "$filename"
	fi

	echo
	echo press any key to preview next file ...
	read anykey < /dev/tty
done < ./input_files_list
