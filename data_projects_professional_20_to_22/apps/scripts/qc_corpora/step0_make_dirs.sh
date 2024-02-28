#!/bin/bash

echo ===== ===== =====
echo step0 creating dirs ...
echo ===== ===== =====

path=`grep ^path config | head -1 | awk '{print $2}'`
mkdir -p $path/failed
mkdir -p $path/passed
mkdir -p $path/step0_source
mkdir -p $path/step1_refine
mkdir -p $path/step2_drop_empty_and_dup
mkdir -p $path/step3_drop_intersection
mkdir -p $path/step4_check_quality
