import configparser
import os
import os.path
import sys


class Config:
	__config_file = 'config.ini'
	__config_dev_file = 'config.dev.ini'


	def __parse_dir(self, config_db):
		self.log_dir = config_db['log_dir']


	def __parse_db(self, config_db):
		self.db_host = config_db['db_host']
		self.db_dbname = config_db['db_dbname']
		self.db_user = config_db['db_user']
		self.db_password = config_db['db_password']


	def __parse_es(self, config_es):
		self.es_host = config_es['es_host']


	def __parse_slack(self, config_slack):
		self.slack_host = config_slack['slack_host']
		self.slack_url = config_slack['slack_url']
		self.slack_channel = '#' + config_slack['slack_channel']
		self.slack_username = config_slack['slack_username']
		self.slack_iconemoji = ':' + config_slack['slack_iconemoji'] + ':'
		self.slack_bot_token = config_slack['slack_bot_token']


	def __parse_bot(self, config_bot):
		self.sample_path_by_bot = config_bot['sample_path_by_bot']


	def __parse_mt(self, config_mt):
		self.mt_host = config_mt['mt_host']
		self.mt_url = config_mt['mt_url']
		self.mt_token = config_mt['mt_token']
		# self.mt_direct_host = config_mt['mt_direct_host']


	def __parse_mt_ibm(self, config_mt_ibm):
		self.mt_ibm_key = config_mt_ibm['mt_ibm_key']
		self.mt_ibm_url = config_mt_ibm['mt_ibm_url']
		self.mt_ibm_version = config_mt_ibm['mt_ibm_version']


	def __parse_mt_textra(self, config_mt_textra):
		self.mt_textra_name = config_mt_textra['mt_textra_name']
		self.mt_textra_key = config_mt_textra['mt_textra_key']
		self.mt_textra_secret = config_mt_textra['mt_textra_secret']

		self.mt_textra_names = [self.mt_textra_name]
		self.mt_textra_keys = [self.mt_textra_key]
		self.mt_textra_secrets = [self.mt_textra_secret]
		if 'mt_textra_name2' in config_mt_textra:
			self.mt_textra_names += [config_mt_textra['mt_textra_name2']]
			self.mt_textra_keys += [config_mt_textra['mt_textra_key2']]
			self.mt_textra_secrets += [config_mt_textra['mt_textra_secret2']]
		if 'mt_textra_name3' in config_mt_textra:
			self.mt_textra_names += [config_mt_textra['mt_textra_name3']]
			self.mt_textra_keys += [config_mt_textra['mt_textra_key3']]
			self.mt_textra_secrets += [config_mt_textra['mt_textra_secret3']]

		self.mt_textra_url_ja_ko = config_mt_textra['mt_textra_url_ja_ko']
		self.mt_textra_url_ko_ja = config_mt_textra['mt_textra_url_ko_ja']
		self.mt_textra_url_ja_ko_colloquial = config_mt_textra['mt_textra_url_ja_ko_colloquial']
		self.mt_textra_url_ko_ja_colloquial = config_mt_textra['mt_textra_url_ko_ja_colloquial']


	def __parse_grammarbot(self, config_grammarbot):
		self.grammarbot_key = config_grammarbot['grammarbot_key']


	def __get_config_file(self):
		python_path = os.environ['PYTHONPATH']

		config_file = self.__config_dev_file if self.__is_dev else self.__config_file
		config_file_p = f'{python_path}/config/{config_file}'
		if os.path.isfile(config_file_p):
			return config_file_p

		config_file_p = f'./{config_file}'
		if os.path.isfile(config_file_p):
			return config_file_p

		return None


	def __init__(self, name, is_dev=False):
		self.name = name
		self.__is_dev = is_dev

		try:
			config_file = self.__get_config_file()
			if not config_file:
				self.is_loaded = False
				return

			config = configparser.ConfigParser()
			config.read(config_file)
			self.__parse_dir(config['DIR'])
			self.__parse_db(config['DB'])
			self.__parse_es(config['ES'])
			self.__parse_slack(config['SLACK'])
			self.__parse_bot(config['BOT'])
			self.__parse_mt(config['MT'])
			self.__parse_mt_ibm(config['MT_IBM'])
			self.__parse_mt_textra(config['MT_TEXTRA'])
			self.__parse_grammarbot(config['GRAMMARBOT'])
			self.is_loaded = True
		except:
			print('[CRITICAL][config.init] %s' % str(sys.exc_info()).replace('"', ' '))
			self.is_loaded = False
