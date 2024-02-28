from corpus_count_parser import CorpusCountParser
from corpus_parser import CorpusParser


class CommandParser:
	__admin = 'jingu.kim'
	__commands = ['언어쌍개수', '코퍼스개수', '샘플요청']
	__lang_names_and_codes = {
		'아랍어': 'ar',
		'독일어': 'de',
		'영어': 'en',
		'스페인어': 'es',
		'프랑스어': 'fr',
		'인도네시아어': 'id',
		'일본어': 'ja',
		'한국어': 'ko',
		'말레이시아어': 'ms',
		'러시아어': 'ru',
		'태국어': 'th',
		'베트남어': 'vi',
		'중국어': 'zh'
	}
	__company_aliases = {
		'애플': 'APPLE',
		'바이두': 'BAIDU',
		'바이트댄스': 'BYTEDANCE',
		'크로스랭귀지': 'CROSSLANGUAGE',
		'이팝소프트': 'EPOPSOFT',
		'에트리': 'ETRI',
		'구글': 'GOOGLE',
		'카카오': 'KAKAO',
		'로그바': 'LOGBAR',
		'메가딕': 'MEGADIC',
		'네이버': 'NAVER',
		'니아': 'NIA',
		'엔티티도코모': 'NTTDOCOMO',
		'엔티티': 'NTTDOCOMO',
		'도코모': 'NTTDOCOMO',
		'시스트란': 'SYSTRAN'
	}


	def is_ready_to_execute(self, text):
		return any([command in text.replace(' ' , '') for command in self.__commands])


	def command(self, texts):
		message = ''
		output_file_with_path = None

		texts_list = texts.replace(' ', '').splitlines()
		if any(['언어쌍개수' in texts_list[0], '코퍼스개수' in texts_list[0]]):
			corpus_count_parser = CorpusCountParser('corpus_count_parser', self.__lang_names_and_codes, self.__langs, self.__admin, self.__db)
			message, output_file_with_path = corpus_count_parser.parse(''.join(texts_list))
		elif '샘플요청' in texts_list[0]:
			corpus_parser = CorpusParser('corpus_parser', self.__lang_names_and_codes, self.__langs, self.__tags, self.__companies, self.__config, self.__db.conn)
			message, output_file_with_path = corpus_parser.parse(texts_list)

		return message, output_file_with_path


	def __init__(self, name, config, db, langs, tags, companies):
		self.name = name
		self.__config = config
		self.__db = db
		self.__langs = langs
		self.__tags = tags
		self.__companies = companies
