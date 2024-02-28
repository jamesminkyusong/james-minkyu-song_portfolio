class LangCodeConverter:
	__iso639_1_and_bcp47 = [
		['ar', 'ar-SA'],
		['de', 'de-DE'],
		['en', 'en-US'],
		['es', 'es-ES'],
		['fr', 'fr-FR'],
		['hi', 'hi-IN'],
		['id', 'id-ID'],
		['ja', 'ja-JP'],
		['ko', 'ko-KR'],
		['ms', 'ms-MY'],
		['pt', 'pt-PT'],
		['ru', 'ru-RU'],
		['th', 'th-TH'],
		['tl', 'fil-PH'],
		['tr', 'tr-TR'],
		['vi', 'vi-VN'],
		['zh', 'zh-CN']
	]


	def __init__(self, name):
		self.name = name
		self.iso639_1_to_bcp47 = lambda code: next((row[1] for row in self.__iso639_1_and_bcp47 if row[0] == code), code) 
		self.bcp47_to_iso639_1 = lambda code: next((row[0] for row in self.__iso639_1_and_bcp47 if row[1] == code), code) 
