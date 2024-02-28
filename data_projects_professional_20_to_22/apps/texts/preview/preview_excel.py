#!../../../bin/python3

from datetime import datetime

import pandas as pd

from cmd_args_preview import CMDArgsPreview
from libs.utils.alert import Alert


def print_df(input_file_with_p, sheet_index, is_all, head, tail):
	print('{} [INFO][preview_excel.get_df] Reading from {} ...'.format(str(datetime.now()), input_file_with_p))

	excel_file = pd.ExcelFile(input_file_with_p)
	sheets_count = len(excel_file.sheet_names)

	df = pd.read_excel(input_file_with_p, header=None, sheet_name=sheet_index)
	cols_count = len(df.columns)
	rows_count = len(df)

	print('===== ===== =====')
	print(f'input_file: {input_file_with_p}')
	print(f'sheets_count: {sheets_count}')
	if sheets_count > 1:
		for i, sheet_name in enumerate(excel_file.sheet_names):
			print('    sheet[{}]: {}'.format(i, excel_file.sheet_names[i]))
	print(f'cols_count: {cols_count}')
	print(f'rows_count: {rows_count}')
	print('===== ===== =====')

	bounds = [range(rows_count)] if is_all else [range(head), range(rows_count-tail, rows_count)]
	for bound in bounds:
		for row_index in bound:
			print(f'row[{row_index}]:')
			for col_index in range(cols_count):
				value = df.iloc[row_index, col_index]
				print(f'    col[{col_index}]: {value}')

	return rows_count


def notify(level, message, is_noti_to_slack):
	level = level.upper()
	print('%s [%s]%s' % (str(datetime.now()), level, message))
	if is_noti_to_slack:
		alert.send(level, '`[%s]` %s' % (level, message))


def main():
	args_preview = CMDArgsPreview('preview_excel', ['input_files'])
	args = args_preview.values

	if args.is_noti_to_slack:
		global alert
		alert = Alert('alert')

	rows_count = 0
	for input_file_with_p in args.input_files_with_p:
		rows_count += print_df(input_file_with_p, args.sheet_index, args.is_all, args.head_count, args.tail_count)

	message = '[preview_excel.main] all rows count is {:,} in {}'.format(rows_count, str(args.input_files))
	notify('info', message, args.is_noti_to_slack)


if __name__ == '__main__':
	main()
