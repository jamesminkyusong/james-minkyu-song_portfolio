#!/bin/bash

while true
do
	count=`ps -ef | grep bot.py | grep -v grep | wc -l`
	if [[ $count -eq 0 ]]
	then
		text=`echo Warning: CorpusBot is dead.`
		json="{\"channel\": \"#corpus_factory\", \"username\": \"corpusbot_guard\", \"icon_emoji\": \":catch:\", \"text\": \"$text\"}"
		curl -s -d "payload=$json" "slackwebhook"
		exit
	fi

	sleep 10
done
