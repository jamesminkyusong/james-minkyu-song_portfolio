#!../../bin/python3

from datetime import datetime
from slack import RTMClient

from command_parser import CommandParser
from config import Config
from libs.utils.db import DB


lang_name_and_code = {
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


@RTMClient.run_on(event='message')
def respond(**payload):
	bot_id = '@USUGW45D4'
	data = payload['data']
	print('%s [DEBUG] data: %s' % (str(datetime.now()), str(data)))
	if 'subtype' in data:
		return

	text = data['text']
	if not text or bot_id not in text:
		return

	user = data['user']
	text = text.replace(bot_id, '')

	channel_id = data['channel']
	web_client = payload['web_client']
	user = data['user']

	command_parser = CommandParser('command_parser', config, db, langs, tags, companies)
	if command_parser.is_ready_to_execute(text):
		web_client.chat_postMessage(
			channel = channel_id,
			text = f'<@{user}> 요청하신 작업을 처리하고 있습니다. 조건에 따라 10분 이상 소요될 수 있기 때문에 여유있게 기다려 주세요. 작업이 끝나면 끝나면 알려 드리겠습니다.'
		)

		message, output_file_with_path = command_parser.command(text)
		web_client.chat_postMessage(
			channel = channel_id,
			text = f'<@{user}> ' + message
		)

		if output_file_with_path:
			web_client.files_upload(
				channels = '#corpus_factory',
				file = output_file_with_path,
				filename = output_file_with_path.split('/')[-1]
			)
	else:
#		web_client.files_upload(
#			channels = '#corpus_factory',
#			file = config.bot_samples_path + '/blue_rabbit.jpg',
#			filename = 'error.jpg'
#		)

		web_client.chat_postMessage(
			channel = channel_id,
			text = f'<@{user}> ' + error_message
		)


def get_error_message(tags, companies):
	return '\n'.join([
		'무슨 말인지 이해할 수 없어요. 아래 양식을 지켜서 요청해 주세요. 지원하는 언어와 도메인, 고객 목록은 아래와 같습니다.',
		'----- ----- -----',
		'지원 언어 : %s',
		'지원 도메인 : %s',
		'납품 고객 : %s',
		'----- ----- -----',
		'@corpus_bot [,(comma)로 분리해서 한국어로 표기] 언어쌍 개수',
		'----- ----- -----',
		'@corpus_bot 샘플 요청',
		'언어쌍 : ,(comma)로 분리해서 한국어로 표기',
		'개수 : 필요한 샘플 개수 (최대 500개)',
		'(생략 가능) 도메인 : 특정 도메인에 속한 문장이 필요한 경우',
		'(생략 가능) 글자수 : 특정 글자수 이상의 문장이 필요한 경우',
		'(생략 가능) 단어수 : 특정 단어수 이상의 문장이 필요한 경우',
		'(생략 가능) 고객 제외 : 특정 고객에게 납품했던 문장을 제외해야 하는 경우',
		'(생략 가능) 포맷 : xlsx, tmx, csv (별도로 지정하지 않을 경우 기본값은 xlsx 입니다.)',
		'----- ----- -----',
		'예#1. 한국어, 영어 언어쌍 개수를 확인할 때',
		'```@corpus_bot 한국어, 영어 언어쌍 개수```',
		'----- ----- -----',
		'예#2. 한국어, 영어, 일본어 언어쌍 개수를 확인할 때',
		'```@corpus_bot 한국어, 영어, 일본어 언어쌍 개수```',
		'----- ----- -----',
		'예#3. 한국어, 영어 언어쌍 100문장이 tmx 포맷으로 필요한 경우',
		'```@corpus_bot 샘플 요청',
		'언어쌍 : 한국어, 영어',
		'개수 : 100개',
		'포맷 : tmx```',
		'----- ----- -----',
		'예#4. 한국어, 영어, 일본어 언어쌍 중 스포츠 200문장이 필요한 경우',
		'```@corpus_bot 샘플 요청',
		'언어쌍 : 한국어, 영어, 일본어',
		'개수 : 200개',
		'도메인 : 스포츠```',
		'----- ----- -----',
		'예#5. 한국어, 영어 언어쌍 중 ETRI에 납품하지 않았던 300문장이 필요한 경우',
		'```@corpus_bot 샘플 요청',
		'언어쌍 : 한국어, 영어',
		'개수 : 300개',
		'고객 제외 : ETRI```',
		'----- ----- -----',
		'예#6. 한국어, 영어 언어쌍 중 한국어가 10단어 이상인 문장 400개가 필요한 경우',
		'```@corpus_bot 샘플 요청',
		'언어쌍 : 한국어, 영어',
		'단어수 : 한국어 10단어',
		'개수 : 400개```'
	]) % (', '.join(sorted(lang_name_and_code.keys())), ', '.join(sorted(tags.keys())), ', '.join(sorted(companies.keys())))


def main():
	global config
	config = Config('config')
	if not config.is_loaded:
		print("[CRITICAL][bot.main] Can't open config.ini.")
		return

	global db
	db = DB('db', config)
	db.open()

	global langs, tags, companies
	langs = db.fetch_languages()
	tags = db.fetch_tags()
	companies = db.fetch_companies()

	global error_message
	error_message = get_error_message(tags, companies)

	rtm_client = RTMClient(token=config.slack_bot_token)
	rtm_client.start()


if __name__ == '__main__':
	main()
