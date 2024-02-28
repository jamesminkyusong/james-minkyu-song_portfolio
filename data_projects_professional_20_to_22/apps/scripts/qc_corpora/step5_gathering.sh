#!/bin/bash

path=`grep ^path config | head -1 | awk '{print $2}'`

echo [1/6] copying empty and dup files ...
cp $path/step2_drop_empty_and_dup/*dup*.xlsx $path/failed
cp $path/step2_drop_empty_and_dup/*empty*.xlsx $path/failed

echo [2/6] copying intersection files ...
cp $path/step3_drop_intersection/*dup*.xlsx $path/failed

echo [3/6] copying bad files ...
cp $path/step4_check_quality/*similarity.xlsx $path/failed
cp $path/step4_check_quality/*bad.xlsx $path/failed
rm $path/failed/*not_bad.xlsx

echo [4/6] copying good files ...
cp $path/step4_check_quality/*not_bad.xlsx $path/passed

echo [5/6] renaming bad files ...
cd $path/failed
ls -al step*.xlsx | awk '{print $9}' > files_list
while read line; do
	new_file=`echo $line | sed -e 's/step[1-4]_//g'`
	mv $line $new_file
done < ./files_list
rm files_list

echo [6/6] renaming not_bad files ...
cd $path/passed
ls -al step*.xlsx | awk '{print $9}' > files_list
while read line; do
	new_file=`echo $line | sed -e 's/step[1-4]_//g' | sed -e 's/_not_bad//g'`
	mv $line $new_file
done < ./files_list
rm files_list
