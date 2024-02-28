#!../../bin/python3

import psycopg2
import sys
from config import Config
from corpus import Corpus
from datetime import datetime
from db import DB
from db2 import DB as DB2
from es import ES
from watch import Watch


def parse_arguments():
	if len(sys.argv) < 3:
		print('Usage: ./insert_voice.sh VOICE_EVENT_ID PARTNER_ID')
		return False, 0, 0

	voice_event_id = int(sys.argv[1])
	partner_id = int(sys.argv[2])

	return True, voice_event_id, partner_id


def main():
	is_valid, voice_event_id, partner_id = parse_arguments()
	if is_valid == False:
		sys.exit()

	global config
	config = Config('config')
	if config.is_loaded == False:
		print("[CRITICAL][insert_voice.main] Can't open config.ini.")
		sys.exit()

	slack = Watch('slack')
	slack.send('info', '`[INFO]` [insert_voice.main] Reading voice event #%d.' % voice_event_id)
	print('%s [INFO][insert_voice.main] Reading voice event #$d.' % (str(datetime.now()), voice_event_id))

	db = DB('db')
	db.open(config)

	db2 = DB2('db2')
	db2.open(config)

	es = ES('es', config.es_host)
	if es.is_connected == False:
		print("[CRITICAL][insert_corpus.main] Can't connect to ElasticSearch.")
		sys.exit()

	print('%s [INFO][insert_voice.main] Fetched: %d rows' % (str(datetime.now()), len(texts1)))

	langs = fetch_languages(db)

	corpus = Corpus("corpus", project_id, db, es, langs)
	for index in range(len(texts1)):
		if index != 0 and index % 1000 == 0:
			print("%s [INFO][insert_corpus.main] Inserted: %d rows" % (str(datetime.now()), index))
		corpus.insert(langs[lang1], texts1[index], langs[lang2], texts2[index])

	db.close()

	slack.send('info', '`[INFO]` [insert_corpus.main] Completed: %d rows from %s' % (len(texts1), filename))


if __name__ == "__main__":
	main()
