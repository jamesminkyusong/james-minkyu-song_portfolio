#!/home/ubuntu/project/OpenNMT-py/bin/python3

from datetime import datetime
from pororo import Pororo
import json
import os
import pandas as pd
import transformers

from cmd_args_classify_topic import CMDArgsClassifyTopic
from libs.utils.df_utils import DFUtils
from libs.utils.reader import Reader


app_name = 'classify_topic'

now_s = lambda: str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
df_utils = DFUtils('df_utils')

classifier = None
max_topics_count = 3
topics = [
	"art",
	"beauty",
	"business",
	"commerce",
	"computer",
	"conversation",
	"customer service",
	"economy",
	"education",
	"engineering",
	"fashion",
	"financial",
	"information technology",
	"law",
	"legal",
	"literature",
 	"liberal arts",
	"marketing",
	"medicine",
	"patent",
	"politics",
	"religion",
	"science",
	"shopping",
	"social media",
	"society",
	"sports",
	"technology",
	"transport",
	"travel",
]
classification_rule = {'all_topics': topics, 'filter_topics': [], 'threshold': 0}


def get_classification_rule(rule_file_p):
	rule = {}

	with open(rule_file_p) as f:
		json_text = json.load(f)
		for key in ['all_topics', 'filter_topics', 'threshold']:
			rule[key] = json_text[key]

	return rule


def classify_topic_by_fb(text):
	global classifier
	result = classifier(text, classification_rule['all_topics'], multi_label=True)
	return result['labels'][0:max_topics_count] + result['scores'][0:max_topics_count]


def classify_topic_by_kk(text):
	global classifier
	result = classifier(text, classification_rule['all_topics'])
	return max(result.items(), key=lambda k: k[1])


def check_result(row, topic_cols, scores_cols, filter_topics, threshold):
	result = False

	for topic_col_n, score_col_n in zip(topic_cols, scores_cols):
		result |= ((row[topic_col_n] in filter_topics) and (row[score_col_n] >= threshold))

	return result


def classify(classify_topic_f, df, text_col_n, filter_topics, threshold, step_interval, path, output_file):
	result_df = pd.DataFrame()

	topics_cols = {i: f'topic_{i+1}' for i in range(0, max_topics_count)}
	scores_cols = {(i+max_topics_count): f'score_{i+1}' for i in range(0, max_topics_count)}
	topics_scores_cols = {**topics_cols, **scores_cols}

	all_count = len(df)
	for step_i, start_i in enumerate(range(0, all_count, step_interval)):
		start_time = datetime.now()
		end_i = min(start_i + step_interval, all_count)

		print('{} [INFO][{}.classify] Classifying {:,} ~ {:,} rows ...'.format(now_s(), app_name, start_i + 1, end_i))
		step_df = df[start_i:end_i].apply(lambda row: classify_topic_f(row[text_col_n]), axis=1, result_type='expand')
		step_df.rename(columns=topics_scores_cols, inplace=True)
		if filter_topics and threshold > 0:
			step_df['result'] = step_df.apply(lambda row: check_result(row, topics_cols.values(), scores_cols.values(), filter_topics, threshold), axis=1)
		result_df = result_df.append(step_df)

		step_output_file = f'_{step_i+1}.'.join(output_file.rsplit('.', 2))
		df_utils.save(pd.concat([df[start_i:end_i], step_df], axis=1), path, step_output_file)

		end_time = datetime.now()
		print('{} [INFO][{}.classify] [{:,}/{:,}] {}% complete ({} secs)'.format(now_s(), app_name, end_i, all_count, int((end_i / all_count) * 100), (end_time - start_time).seconds))

	return result_df


def main():
	args_classify_topic = CMDArgsClassifyTopic('cmd_args_classify_topic', ['lang', 'text_col_n'])
	args = args_classify_topic.values

	global classification_rule
	if args.rule_file:
		rule_file_p = f'{args.path}/{args.rule_file}'
		if os.path.exists(rule_file_p):
			classification_rule = get_classification_rule(rule_file_p)

	reader = Reader('reader')
	df = reader.get_simple_df(args.input_files_p[0])
	print('{} [INFO][{}.main] {:,} rows fetched'.format(now_s(), app_name, len(df)))

	global classifier
	if args.method == 'kakao':
		print('{} [INFO][{}.main] zero-shot-library : kakao'.format(now_s(), app_name))
		classifier = Pororo(task='zero-topic', lang='en')
		classify_topic_f = classify_topic_by_kk
	else:
		print('{} [INFO][{}.main] zero-shot-library : facebook'.format(now_s(), app_name))
		classifier = transformers.pipeline('zero-shot-classification', model='facebook/bart-large-mnli', device=0)
		classify_topic_f = classify_topic_by_fb

	result_df = classify(
		classify_topic_f,
		df,
		args.text_col_n,
		classification_rule['filter_topics'],
		classification_rule['threshold'],
		len(df) if args.step_interval == 0 else args.step_interval,
		args.path,
		args.output_file
	)

	if args.step_interval > 0 and len(df) > args.step_interval:
		df_utils.save(
			pd.concat([df, result_df], axis=1),
			args.path,
			args.output_file
		)


if __name__ == '__main__':
	main()
