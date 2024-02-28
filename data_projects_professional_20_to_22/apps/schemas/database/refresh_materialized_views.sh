#!/bin/bash

text=`echo Refreshing : m_parallel_corpus_2 ...`
json="{\"channel\": \"#monologue_of_jin\", \"username\": \"CMS\", \"icon_emoji\": \":flitto:\", \"text\": \"$text\"}"
curl -s -d "payload=$json" "https://hooks.slack.com/services/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"
psql -U flitto -h 54.191.70.237 -c "REFRESH MATERIALIZED VIEW m_parallel_corpus_2"
text=`echo Refreshing completed : m_parallel_corpus_2!`
json="{\"channel\": \"#monologue_of_jin\", \"username\": \"CMS\", \"icon_emoji\": \":flitto:\", \"text\": \"$text\"}"
curl -s -d "payload=$json" "https://hooks.slack.com/services/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"

text=`echo Refreshing : m_parallel_corpus_3 ...`
json="{\"channel\": \"#monologue_of_jin\", \"username\": \"CMS\", \"icon_emoji\": \":flitto:\", \"text\": \"$text\"}"
curl -s -d "payload=$json" "https://hooks.slack.com/services/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"
psql -U flitto -h 54.191.70.237 -c "REFRESH MATERIALIZED VIEW m_parallel_corpus_3"
text=`echo Refreshing completed : m_parallel_corpus_3!`
json="{\"channel\": \"#monologue_of_jin\", \"username\": \"CMS\", \"icon_emoji\": \":flitto:\", \"text\": \"$text\"}"
curl -s -d "payload=$json" "https://hooks.slack.com/services/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"

text=`echo Refreshing : m_parallel_corpus_4 ...`
json="{\"channel\": \"#monologue_of_jin\", \"username\": \"CMS\", \"icon_emoji\": \":flitto:\", \"text\": \"$text\"}"
curl -s -d "payload=$json" "https://hooks.slack.com/services/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"
psql -U flitto -h 54.191.70.237 -c "REFRESH MATERIALIZED VIEW m_parallel_corpus_4"
text=`echo Refreshing completed : m_parallel_corpus_4!`
json="{\"channel\": \"#monologue_of_jin\", \"username\": \"CMS\", \"icon_emoji\": \":flitto:\", \"text\": \"$text\"}"
curl -s -d "payload=$json" "https://hooks.slack.com/services/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"
