#!/bin/bash

#
# Should execute the below script before updating texts in DB and ES
# This script saves cleaned texts only in an excel file
#
# apps/texts/manipulate_excel/leave_cleaned_text_only.sh LANG_CODE
#

lang_code=$1

path=`echo ~/project/corpus_raw/texts/mono`
input_file=`echo mono_ $lang_code _cleaned_only.xlsx | sed -e 's/ //g'`
corpus_id=`echo $lang_code _id | sed -e 's/ //g'`

echo ===== ===== =====
echo $lang_code : updating texts in DB and ES ...
echo ===== ===== =====
./update_corpus.py -p $path -i $input_file --col_indices 2 3 --col_names $corpus_id $lang_code -s
