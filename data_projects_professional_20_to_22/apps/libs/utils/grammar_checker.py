from grammarbot import GrammarBotClient

from config import Config


class GrammarChecker:
	def correct(self, text):
		corrected_texts = []

		response = self.__client.check(text)
		matches = response.matches
		if matches:
			corrected_texts = sum([[correction for correction in match.corrections] for match in matches], [])

		return corrected_texts


	def __init__(self, name):
		self.name = name
		config = Config('config')
		self.__client = GrammarBotClient(api_key=config.grammarbot_key)
