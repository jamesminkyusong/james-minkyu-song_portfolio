#!/bin/bash

echo ===== ===== =====
echo counting mono corpora ...
echo ===== ===== =====

./count_corpus.py \
	-p ~/project/corpus_raw/texts/multi_pairs \
	-o stat_mono.xlsx \
	--x_pairs 1 \
	--update_db \
	--save_excel \
	--prod

text=`echo [INFO] counting mono corpora is complete!`
json="{\"channel\": \"#corpus_log\", \"username\": \"corpus\", \"icon_emoji\": \":corpus:\", \"text\": \"$text\"}"
curl -s -d "payload=$json" "slack webhook"

echo ===== ===== =====
echo counting 2-pair corpora ...
echo ===== ===== =====

./count_corpus.py \
	-p ~/project/corpus_raw/texts/multi_pairs \
	-o stat_2pairs.xlsx \
	--x_pairs 2 \
	--update_db \
	--save_excel \
	--prod

text=`echo [INFO] counting 2-pair corpora is complete!`
json="{\"channel\": \"#corpus_log\", \"username\": \"corpus\", \"icon_emoji\": \":corpus:\", \"text\": \"$text\"}"
curl -s -d "payload=$json" "slack webhook"
