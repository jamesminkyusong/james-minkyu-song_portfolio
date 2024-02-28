#!/bin/bash

path=`echo ~/project/corpus_raw/speeches`

./speech_stat.py \
	-p $path \
	--events_file new_events_list \
	--prod
