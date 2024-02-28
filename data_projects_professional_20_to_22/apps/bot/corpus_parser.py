import re

from libs.corpus.parallel_corpus import ParallelCorpus
from libs.utils.code_books import FileFormat
from libs.utils.request_format import RequestFormat


class CorpusParser:
	__admin = 'jingu.kim'
	__max_rows = 500
	__tag_aliases = {
		'IT/소프트웨어': 'IT',
		'금융/경제': 'finance',
		'기타': 'etc',
		'법률/특허/계약': 'legal',
		'비즈니스': 'business',
		'스포츠': 'sports',
		'여행/쇼핑': 'travel_shopping',
		'의학': 'medical',
		'일상 대화': 'daily_conversation'
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


	def parse(self, texts):
		lang_text = next((text for text in texts if '언어쌍:' in text), None)
		if not lang_text:
			return '언어쌍 항목이 없습니다. 언어쌍은 필수입니다.', None

		count_text = next((text for text in texts if '개수:' in text), None)
		if not count_text:
			return '개수 항목이 없습니다. 개수는 필수입니다.', None

		parse_texts = [lang_text, count_text]
		parse_funcs = [self.__parse_langs, self.__parse_count]
		keywords_and_funcs = [
			['도메인:', self.__parse_tag],
			['글자수:', self.__parse_min_chars_count],
			['단어수:', self.__parse_min_words_count],
			['고객제외:', self.__parse_company],
			['포맷:', self.__parse_format]
		]
		for keyword, func in keywords_and_funcs:
			text = next((text for text in texts if keyword in text), None)
			if text:
				parse_texts.append(text)
				parse_funcs.append(func)

		req = RequestFormat('request_format')
		for text, func in zip(parse_texts, parse_funcs):
			message, req = func(text, req)
			if message:
				return message, None

		req.path = self.__path
		output_file = '%s_samples_%d' % ('_'.join(req.lang_codes), req.count)
		if req.tag_name:
			output_file += f'_{req.tag_name}'
		output_file += f'.{req.output_file_format.value}'
		req.output_file = output_file

		parallel_corpus = ParallelCorpus('parallel_corpus', self.__conn)
		parallel_corpus.fetch(req, None, 0, None, is_newest=True, is_add_ids=False, is_add_source=False, is_add_tag=False)

		message = ''
		if req.exclude_company_id > 0:
			message += '%s에 납품하지 않은 ' % req.exclude_company_name
		message += ', '.join(req.lang_names) + ' '
		if req.tag_id > 0:
			message += req.tag_name + ' '
		message += '샘플 {:,}개입니다.'.format(req.count)

		return message, '%s/%s' % (req.path, req.output_file)


	def __parse_langs(self, text, req):
		lang_names = text.split(':')[1].split(',')
		if len(lang_names) < 2:
			return '언어는 2개 이상이어야 합니다.', None

		not_supported_lang_names = [lang_name for lang_name in lang_names if lang_name not in self.__lang_names_and_codes]
		if not_supported_lang_names:
			message = (
				'%s는 지원하지 않습니다.\n'
				'현재 지원하는 언어는 %s 입니다.'
			) % (', '.join(not_supported_lang_names), ', '.join(self.__lang_names_and_codes.keys()))
			return message, None

		lang_pairs = []
		for lang_name in lang_names:
			lang_code = self.__lang_names_and_codes[lang_name]
			lang_id = self.__langs[lang_code]
			lang_pairs.append([lang_id, lang_code, lang_name])
		lang_pairs.sort()

		req.lang_ids, req.lang_codes, req.lang_names = zip(*lang_pairs)

		return None, req


	def __parse_count(self, text, req):
		count = re.findall(r'\d+', text)
		if not count:
			return '개수가 명확하지 않습니다. 다시 입력해 주세요.', None

		count_int = int(count[0])
		if 0 < count_int <= self.__max_rows:
			req.count = count_int
		else:
			message = (
				f'샘플은 {self.__max_rows}개까지 추출할 수 있습니다.'
				f'더 많은 샘플이 필요하시면 <@{self.__admin}> 에게 DM 주세요.'
			)
			return message, None

		return None, req


	def __parse_tag(self, text, req):
		tag_name = text.split(':')[1]
		tag_key = next((key for key in self.__tags.keys() if tag_name.upper() in key), None)
		if not tag_key:
			message = (
				f'{tag_name}은(는) 지원하지 않습니다.\n'
				'현재 지원하는 도메인은 %s 입니다.'
			) % ', '.join(sorted(self.__tags.keys()))
			return message, None

		req.tag_id = self.__tags[tag_key]
		req.tag_name = self.__tag_aliases[tag_key]
		return None, req


	def __parse_min_chars_count(self, text, req):
		min_chars_count = re.findall(r'\d+', text)
		if not min_chars_count:
			return '최소 글자수가 명확하지 않습니다. 다시 입력해 주세요.', None

		req.min_chars_count = int(min_chars_count[0])
		return None, req


	def __parse_min_words_count(self, text, req):
		min_words_count = re.findall(r'\d+', text)
		if not min_words_count:
			return '최소 단어수가 명확하지 않습니다. 다시 입력해 주세요.', None

		req.min_words_count = int(min_words_count[0])
		return None, req


	def __parse_company(self, text, req):
		company_name = text.split(':')[1]
		new_company_name = self.__company_aliases.get(company_name, company_name)

		if not any([new_company_name in key for key in self.__companies.keys()]):
			message = (
				f'{company_name}은(는) 고객 목록에 없습니다.\n'
				'선택할 수 있는 고객은 고객은 %s 입니다.'
			) % ', '.join(sorted(self.__companies.keys()))
			return message, None

		req.exclude_company_id = self.__companies[new_company_name]
		req.exclude_company_name = company_name

		return None, req


	def __parse_format(self, text, req):
		req.output_file_format = FileFormat(next((item.value for item in FileFormat if item.value in text), 'xlsx'))
		return None, req


	def __init__(self, name, lang_names_and_codes, langs, tags, companies, config, conn):
		self.name = name
		self.__lang_names_and_codes = lang_names_and_codes
		self.__langs = langs
		self.__tags = tags
		self.__companies = companies
		self.__config = config
		self.__conn = conn
		self.__path = config.sample_path_by_bot
