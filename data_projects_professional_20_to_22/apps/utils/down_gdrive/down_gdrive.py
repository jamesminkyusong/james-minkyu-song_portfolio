#!../../../bin/python3

from datetime import datetime
import glob
import io
import os.path
import pickle

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from getfilelistpy import getfilelist
import pandas as pd

from cmd_args_down_gdrive import CMDArgsDownGdrive
from libs.utils.df_utils import DFUtils


app_name = 'down_gdrive'
now_s = lambda: str(datetime.now())


def fetch_sub_dirs(path, output_file, names, gdrive_ids):
	df = pd.DataFrame({
		'name': names,
		'gdrive_id': gdrive_ids})
	df_utils = DFUtils('df_utils')
	df_utils.save(df, path, output_file)

	dup_df = df[df['name'].duplicated(keep=False)]
	if (dup_count := len(dup_df)) > 0:
		print('{} [CRITICAL][{}.fetch_sub_dirs] {} folders are duplicates ...'.format(now_s(), app_name, dup_count))
		dup_output_file = '_dup.'.join([*output_file.rsplit('.', 1)])
		df_utils.save(dup_df, path, dup_output_file)


def filter_files(files_list, exts):
	print('{} [INFO][{}.filter_files] Filtering by extentions: {} ...'.format(now_s(), app_name, exts))
	matched_list = []

	for ext in exts:
		matched_list += list(filter(lambda a_file: len(a_file['name']) >= len(ext)+2 and a_file['name'][-len(ext):].lower() == ext, files_list))

	if (filtered_count := len(files_list) - len(matched_list)) > 0:
		message = '{:,} files filtered'.format(filtered_count)
	else:
		message = 'Nothing filtered'
	print('{} [INFO][{}.filter_files] {}'.format(now_s(), app_name, message))

	return matched_list


def download_files(drive_service, path, files_list):
	files_count = len(files_list)
	for i, a_file in enumerate(files_list):
		file_id = a_file['id']
		filename = a_file['name']
		print('{} [INFO][{}.download_files] [{}/{}] id  : {}'.format(now_s(), app_name, i+1, files_count, file_id))
		print('{} [INFO][{}.download_files] [{}/{}] name: {}'.format(now_s(), app_name, i+1, files_count, filename))

		request = drive_service.files().get_media(fileId=file_id)
		fh = io.FileIO(path + '/' + filename, 'wb')
		downloader = MediaIoBaseDownload(fh, request)
		done = False
		while not done:
			status, done = downloader.next_chunk()
			print('{} [INFO][{}.download_files] download {}%'.format(now_s(), app_name, int(status.progress() * 100)))


def compare_files_list(path, gdrive_files):
	print('{} [INFO][{}.compare_files_list] Checking files count ...'.format(now_s(), app_name))

	files_list_p = glob.glob(path + '/*')
	files_list = set(map(lambda filename: filename.split('/')[-1], files_list_p))
	fail_files = list(gdrive_files - files_list)
	if fail_files:
		for fail_file in fail_files:
			print('{} [CRITICAL][{}.compare_files_list] not found file: {}'.format(now_s(), app_name, fail_file))
	else:
		print('{} [INFO][{}.compare_files_list] all downloads are complete.'.format(now_s(), app_name))


def main():
	SCOPES = ['https://www.googleapis.com/auth/drive']
	creds = None
	credFile = 'token.pickle'
	
	args_down_gdrive = CMDArgsDownGdrive('cmd_args_down_gdrive', ['drive_id'])
	args = args_down_gdrive.values
	
	if os.path.exists(credFile):
		with open(credFile, 'rb') as token:
			creds = pickle.load(token)
	
	if not creds or not creds.valid:
		if creds and creds.expired and creds.refresh_token:
			creds.refresh(Request())
		else:
			flow = InstalledAppFlow.from_client_secrets_file('../../config/gdrive_credentials.json', SCOPES)
			creds = flow.run_local_server()
		with open(credFile, 'wb') as token:
			pickle.dump(creds, token)
	
	resource = {
		"oauth2": creds,
		"id": args.drive_id,
		"fields": "files(name, id)",
	}
	
	res = getfilelist.GetFileList(resource)
	drive_service = build('drive', 'v3', credentials=creds)

	if args.is_fetch_sub_dirs:
		fetch_sub_dirs(
			args.path,
			args.output_file,
			res['folderTree']['names'],
			res['folderTree']['folders'])
	elif args.is_download:
		files_list = res['fileList'][0]['files']
		if args.extentions:
			files_list = filter_files(files_list, args.extentions)
		download_files(drive_service, args.path, files_list)
		compare_files_list(args.path, set(map(lambda a_file: a_file['name'], files_list)))


if __name__ == '__main__':
	main()
