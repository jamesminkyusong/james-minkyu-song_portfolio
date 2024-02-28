#!../../../bin/python3

from datetime import datetime
import os
import sys
import wget

from cmd_opts_downloader import CMDOptsDownloader
from libs.excel.excel import Excel
from libs.utils.alert import Alert


def down(path, input_file, sheet_index, col_indices, col_names, start_row):
	print('%s [INFO][downloader.down] Reading from %s ...' % (str(datetime.now()), input_file))

	excel = Excel('excel')
	rows = excel.read('%s/%s' % (path, input_file), sheet_index, col_indices, col_names, start_row)

	for index, row in enumerate(rows):
		sid, user_id, url = int(row[0]), row[1], row[2]
		user_path = f'{path}/{user_id}'
		if not os.path.exists(user_path):
			os.makedirs(user_path)

		url = url.replace('flittosg.s3.amazonaws.com', 'i.fltcdn.net')
		output_file = f'{user_id}_{sid}.'
		if url[-3:] == 'pcm':
			output_file += 'wav'
		else:
			output_file += url[-3:]

		print('%s [INFO][downloader.down][%d / %d] Downloading %s ...' % (str(datetime.now()), index + 1, len(rows), url))
		wget.download(url, f'{user_path}/{output_file}')


def notify(level, message, is_noti_to_slack):
	level = level.upper()
	print('%s [%s]%s' % (str(datetime.now()), level, message))
	if is_noti_to_slack:
		alert.send(level, '`[%s]` %s' % (level, message))


def main():
	opts = CMDOptsDownloader('opts', sys.argv[1:])
	if not opts.is_loaded:
		return

	if opts.is_noti_to_slack:
		global alert
		alert = Alert('alert')

	for input_file in opts.input_files:
		down(opts.path, input_file, 0, opts.col_indices, opts.col_names, 1)

	notify('info', '[2_downloader.main] All files downloaded!', opts.is_noti_to_slack)


if __name__ == '__main__':
	main()
