#!../../../bin/python3

from datetime import datetime

import pandas as pd
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch.nn.functional as F

from cmd_args_classify_hate import CMDArgsClassifyHate


app_name = 'classify_hate'

huggingface_model = 'beomi/korean-hatespeech-classifier'
index2label = ['None', 'Hate', 'Offensive']
now_s = lambda: str(datetime.now())


def main():
	args_classify_hate = CMDArgsClassifyHate('cmd_args_classify_hate', ['lang', 'check_col_n'])
	args = args_classify_hate.values

	tokenizer = AutoTokenizer.from_pretrained(huggingface_model)
	model = AutoModelForSequenceClassification.from_pretrained(huggingface_model)
	model.eval()

	df = pd.read_excel(args.input_files_with_p[0])
	all_count = len(df)

	label_list, value_list = [], []
	for row_i, text in enumerate(df[args.check_col_n]):
		tokenized_text = tokenizer([text], return_tensors='pt')
		output = model(**tokenized_text)
		values = F.softmax(output['logits'][0], dim=-1).detach().tolist()
		max_value = max(values)
		index = values.index(max_value)
		label_list += [index2label[index]]
		value_list += [max_value]

		if row_i > 0 and ((row_i + 1) % 1_000 == 0 or (row_i + 1) == all_count):
			print(f'{now_s()} [INFO][{app_name}.main] [{row_i+1}/{all_count}] {int(row_i*100/all_count)}% complete')

	df['label'] = label_list
	df['value'] = value_list

	writer = pd.ExcelWriter(f'{args.path}/{args.output_file}', engine='xlsxwriter')
	df.to_excel(writer, index=False)
	writer.save()


if __name__ == '__main__':
	main()
