#!../../../bin/python3

from datetime import datetime
import sys
import pandas as pd

from cmd_opts_formatter import CMDOptsFormatter
from libs.excel.excel import Excel
from libs.utils.df_utils import DFUtils


def get_df(path, input_file, sheet_index, col_indices, col_names, start_row):
	print('%s [INFO][formatter.get_df] Reading from %s ...' % (str(datetime.now()), input_file))

	excel = Excel('excel')
	rows = excel.read('%s/%s' % (path, input_file), sheet_index, col_indices, col_names, start_row)
	df = pd.DataFrame(rows, columns=col_names)

	print('%s [INFO][formatter.get_df] Fetched %d rows in %s' % (str(datetime.now()), len(df), input_file))
	return df


def rename_users(df, col_name):
	print('%s [INFO][formatter.rename_users] Renaming %s ...' % (str(datetime.now()), col_name))

	user_index = 0
	renamed_user = f'user{user_index}'
	current_user = ''

	new_rows = []
	for index, row in enumerate(df[col_name].values):
		if row[0] != current_user:
			user_index += 1
			renamed_user = f'user{user_index}'
			current_user = row
		new_rows.append(renamed_user)
		if (index + 1) % 1000 == 0:
			print('%s [INFO][formatter.rename_users] %d / %d renamed!' % (str(datetime.now()), (index + 1), len(df)))

	df[col_name] = new_rows

	print('%s [INFO][formatter.rename_users] Renaming completed!' % str(datetime.now()))
	return df


def notify(level, message, is_noti_to_slack):
	level = level.upper()
	print('%s [%s]%s' % (str(datetime.now()), level, message))
	if is_noti_to_slack:
		alert.send(level, '`[%s]` %s' % (level, message))


def main():
	opts = CMDOptsFormatter('opts', sys.argv[1:])
	if not opts.is_loaded:
		return

	if opts.is_noti_to_slack:
		global alert
		alert = Alert('alert')

	all_df = None
	for input_file in opts.input_files:
		df = get_df(opts.path, input_file, 0, opts.col_indices, opts.col_names, 1)
		all_df = df if all_df is None else pd.concat([all_df, df])

	df_utils = DFUtils('df_utils')
	df_utils.sort(all_df, [opts.col_names[0]])
	all_df = rename_users(all_df, [opts.col_names[0]])

	df_utils.add_sid(all_df)
	df_utils.save(all_df, opts.path, opts.output_file, opts.max_rows_in_file)

	message = '[formatter.main] %d rows saved in %s!' % (len(all_df), opts.output_file)
	notify('info', message, opts.is_noti_to_slack)


if __name__ == '__main__':
	main()
