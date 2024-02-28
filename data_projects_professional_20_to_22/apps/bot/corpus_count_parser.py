from libs.corpus.corpus_stat import CorpusStat


class CorpusCountParser:
	def parse(self, texts):
		lang_pairs = []
		for name, code in self.__lang_names_and_codes.items():
			if name in texts:
				lang_id = self.__lang_codes_and_ids[code]
				lang_pairs.append([lang_id, code, name])

		if len(lang_pairs) > 3:
			return f'3개 언어까지 코퍼스 개수를 확인할 수 있습니다. 4개 언어 이상에 대한 코퍼스 개수를 원하시면 <@{self.__admin}> 에게 DM 주세요.', None

		if len(lang_pairs) < 1:
			return '1개 이상의 언어를 입력해 주세요.\n' \
				+ '현재 지원하는 언어는 %s 입니다.' % ', '.join(sorted(self.__lang_names_and_codes.keys())), None

		lang_pairs.sort()
		lang_ids = [lang[0] for lang in lang_pairs]
		corpus_stat = CorpusStat('corpus', self.__db)
		count = corpus_stat.fetch(*lang_ids)

		message = ', '.join([lang[2] for lang in lang_pairs])
		message += ' 코퍼스 개수는 {:,}개입니다.'.format(count)
		return message, None


	def __init__(self, name, lang_names_and_codes, lang_codes_and_ids, admin, db):
		self.name = name
		self.__lang_names_and_codes = lang_names_and_codes
		self.__lang_codes_and_ids = lang_codes_and_ids
		self.__admin = admin
		self.__db = db
