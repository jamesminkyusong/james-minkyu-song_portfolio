#!/bin/bash

lang_pairs=$1
if [ $lang_pairs == "ko2en" ]; then
	drive_id=`echo key`
elif [ $lang_pairs == "ko2ja" ]; then
	drive_id=`echo key`
elif [ $lang_pairs == "ko2zh" ]; then
	drive_id=`echo key`
else
	echo ERROR: Unknown lang_pairs \($lang_pairs\)!
	return
fi

now=`date +'%Y%m%d %H:%M:%S'`
echo ===== ===== =====
echo $now Monitoring started!
echo ===== ===== =====

current_files_list=`echo $lang_pairs.current`
new_files_list=`echo $lang_pairs.new`
diff_files_list=`echo $lang_pairs.diff`

while true; do
	./drive_mon.py --drive_id $drive_id > ./$lang_pairs
	cat $lang_pairs | sed 's/, /\n/g' | grep xlsx | cut -d\' -f4 | sed 's/ //g' > $new_files_list
	if [ `wc -l $new_files_list | wc -l` -eq 0 ]; then
		continue
	fi
	diff $new_files_list $current_files_list | grep '<' | awk '{print $2}' > $diff_files_list

	while read line; do
		text=`echo New $lang_pairs uploaded : $line`
		json="{\"channel\": \"#corpus_log\", \"username\": \"corpus\", \"icon_emoji\": \":corpus:\", \"text\": \"$text\"}"
		curl -s -d "payload=$json" "https://hooks.slack.com/services/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"
	done < ./$diff_files_list

	if [ `wc -l $new_files_list | wc -l` -ge 1 ]; then
		mv $new_files_list $current_files_list
	fi

	now=`date +'%Y%m%d %H:%M:%S'`
	sleep_seconds=`shuf -i 3600-7200 -n 1`
	echo $now This script will be executed after $sleep_seconds seconds ...
	sleep $sleep_seconds
done
