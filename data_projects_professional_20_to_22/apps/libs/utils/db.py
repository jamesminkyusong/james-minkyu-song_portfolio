import sys
import psycopg2

from libs.utils.alert import Alert


class DB:
	def open(self):
		try:
			self.conn = psycopg2.connect(
				host = self.__config.db_host,
				dbname = self.__config.db_dbname,
				user = self.__config.db_user,
				password = self.__config.db_password
			)
			self.cursor = self.conn.cursor()
		except:
			self.__alert.send('critical', '`[CRITICAL]` [DB.open] %s' % str(sys.exc_info()).replace('"', ' '))


	def close(self):
		try:
			self.cursor.close()
			self.conn.close()
		except:
			self.__alert.send('minor', '`[MINOR]` [DB.close] %s' % str(sys.exc_info()).replace('"', ' '))


	def fetch_all(self, query, values):
		self.cursor.execute(query, values)
		return self.cursor.fetchall()


	def fetch_row(self, query, values):
		self.cursor.execute(query, values)
		return self.cursor.fetchone()


	def execute(self, query, values):
		self.cursor.execute(query, values)
		row = self.cursor.fetchone()
		self.conn.commit()

		return row if row is not None else []


	def execute_without_return(self, query, values):
		self.cursor.execute(query, values)
		self.conn.commit()


	def fetch_languages(self):
		query = ' \
			SELECT code, id \
			FROM languages \
		'

		return self.__fetch_codes(query)


	def fetch_companies(self):
		query = ' \
			SELECT company, id \
			FROM partners \
		'

		return self.__fetch_codes(query)


	def fetch_tags(self):
		query = ' \
			SELECT name, id \
			FROM tags \
		'

		return self.__fetch_codes(query)


	def __fetch_codes(self, query):
		self.cursor.execute(query)
		rows = self.cursor.fetchall()

		codes = {}
		for row in rows:
			codes[row[0]] = int(row[1])

		return codes


	def fetch_corpus_by_lang_id(self, lang_id):
		query = "SELECT REGEXP_REPLACE(text, '[\r\n]', ' ', 'g') \
			FROM corpus \
			WHERE lang_id = %d \
			ORDER BY id" % lang_id
		return self.fetch_all(query, ())


	def __init__(self, name, config):
		self.name = name
		self.__config = config
		self.__alert = Alert('alert')
