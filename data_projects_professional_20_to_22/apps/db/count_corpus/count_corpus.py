#!../../../bin/python3

from datetime import datetime
import itertools

from cmd_args_count import CMDArgsCount
from config import Config
from libs.corpus.corpus_stat import CorpusStat
from libs.corpus.parallel_corpus import ParallelCorpus
from libs.utils.alert import Alert
from libs.utils.db import DB
from libs.utils.df_utils import DFUtils


def calc_corpus_count(langs, lang_codes, parallel_corpus, exclude_company_ids):
	lang_ids = [langs[lang_code] for lang_code in lang_codes]
	lang_pairs = sorted(zip(lang_ids, lang_codes))
	total_count, count_per_tag = parallel_corpus.fetch_count(
		[x[0] for x in lang_pairs],
		[x[1] for x in lang_pairs],
		exclude_company_ids)

	return [x[1] for x in lang_pairs], total_count, count_per_tag


def notify(level, message, is_noti_to_slack):
	level = level.upper()
	print('%s [%s]%s' % (str(datetime.now()), level, message))
	if is_noti_to_slack:
		alert.send(level, f'`[{level}]` {message}')


def main():
	args_count = CMDArgsCount('cmd_args_count')
	args = args_count.values

	config = Config('config', is_dev=not args.is_production)
	if not config.is_loaded:
		print('[CRITICAL][count_corpus.main] Can\'t open config.ini.')
		return

	if args.is_noti_to_slack:
		global alert
		alert = Alert('alert')

	db = DB('db', config)
	db.open()

	corpus_stat = CorpusStat('corpus_stat', db)

	langs_with_code_key = db.fetch_languages()
	langs_with_id_key = {value: key for key, value in langs_with_code_key.items()}
 
	if args.x_pairs:
		lang_ids = sorted(list(langs_with_id_key.keys()))

		matrix = [lang_ids] * args.x_pairs
		if args.x_pairs == 2:
			select_lang_codes_list = [list(map(lambda y: langs_with_id_key[y], x)) \
				for x in itertools.product(*matrix) if x[1] > x[0]]
		elif args.x_pairs == 3:
			select_lang_codes_list = [list(map(lambda y: langs_with_id_key[y], x)) \
				for x in itertools.product(*matrix) if x[2] > x[1] > x[0]]
		elif args.x_pairs == 4:
			select_lang_codes_list = [list(map(lambda y: langs_with_id_key[y], x)) \
				for x in itertools.product(*matrix) if x[3] > x[2] > x[1] > x[0]]
		else:
			select_lang_codes_list = [[langs_with_id_key[lang_id]] for lang_id in lang_ids]

		if args.is_update_db:
			parallel_corpus = ParallelCorpus('parallel_corpus', db)
			corpus_stat.clear(args.x_pairs)
			for select_lang_codes in select_lang_codes_list:
				print('%s [INFO][count_corpus.main] Calculating the count of %s corpora ...' % (str(datetime.now()), str(select_lang_codes)))
				sorted_lang_codes, total_count, count_per_tag = calc_corpus_count(
					langs_with_code_key,
					select_lang_codes,
					parallel_corpus,
					args.exclude_company_ids)
				if total_count > 0 and 1 <= len(select_lang_codes) <= 3:
					select_lang_ids = [langs_with_code_key[x] for x in select_lang_codes]
					corpus_stat.update(select_lang_ids, count_per_tag)
				message = '[count_corpus.main] The count of {} corpora : {:,} {}'.format(str(sorted_lang_codes), total_count, str(count_per_tag))
				notify('info', message, args.is_noti_to_slack)

		if args.is_save_excel:
			if args.x_pairs == 2:
				df = corpus_stat.fetch_2pairs_all_df()
			else:
				df = corpus_stat.fetch_mono_all_df()
			df_utils = DFUtils('df_utils')
			df_utils.save(df, args.path, args.output_file)
	else:
		lang_ids = sorted([langs_with_code_key[lang_code] for lang_code in args.lang_codes])
		total_count = corpus_stat.fetch(lang_ids)
		message = '[count_corpus.main] The count of {} corpora : {:,}'.format(str(sorted(args.lang_codes)), total_count)
		notify('info', message, args.is_noti_to_slack)

	db.close()


if __name__ == '__main__':
	main()
