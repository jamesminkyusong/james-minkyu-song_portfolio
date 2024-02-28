import certifi
import sys
from datetime import datetime
from elasticsearch import Elasticsearch


class ES:
	index_prefix = 'corpus'


	def insert(self, lang_code, corpus_id, text):
		inserted = False
		error = None

		try:
			body = { \
				'corpus_id': str(corpus_id), \
				'text': self.clean(text) \
			}
			response = self.es.index(index = self.index_prefix + f'_{lang_code}', \
				doc_type = 'texts', \
				id = corpus_id, \
				body = body)

			inserted = response['result'] in ['created', 'updated']
		except:
			error = '[es.insert] %s' % str(sys.exc_info()).replace('"', ' ')
			print('%s [CRITICAL]%s' % (str(datetime.now()), error))

		return inserted, error


	def find(self, lang_code, text):
		corpus_id = 0
		error = None

		try:
			body = { 'query': \
				{ 'match': \
					{ 'text.keyword': self.clean(text) } \
				} \
			}
			response = self.es.search(index = self.index_prefix + f'_{lang_code}', \
				body = body)

			hits = response['hits']
			hits_total = hits['total']
			if hits_total >= 1:
				corpus_id = int(hits['hits'][0]['_source']['corpus_id'])
		except:
			error = '[es.find] %s' % str(sys.exc_info()).replace('"', ' ')
			print('%s [CRITICAL]%s' % (str(datetime.now()), error))

		return corpus_id, error


	def delete_by_corpus_id(self, lang_code, corpus_id):
		try:
			body = { "query": \
				{ "match": \
					{ "corpus_id.keyword": corpus_id } \
				} \
			}
			self.es.delete_by_query(index = self.index_prefix + ("_%s" % lang_code), \
				doc_type = "texts", \
				body = body)
		except:
			error = '[es.delete_by_corpus_id] %s' % str(sys.exc_info()).replace('"', ' ')
			print('%s [CRITICAL]%s' % (str(datetime.now()), error))


	def clean(self, text):
		return text.strip().replace('"', '\\\"')


	def __init__(self, name, host):
		self.name = name

		try:
			if host:
				self.es = Elasticsearch([host], use_ssl = True, ca_certs = certifi.where())
				self.is_connected = True
			else:
				self.is_connected = False
		except:
			print('%s [CRITICAL][es.init] %s' % (str(datetime.now()), str(sys.exc_info()).replace('"', ' ')))
			self.is_connected = False
