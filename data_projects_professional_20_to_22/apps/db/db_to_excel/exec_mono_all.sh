#!/bin/bash

langs=`echo ar de en es fr hi id it ja ko ms ne pl pt ru th tl tr vi zh`

for lang1 in `echo $langs`; do
	./exec_multi_pairs.sh $lang1
done
