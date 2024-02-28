#!../../../bin/python3

import glob
import io
import os.path
import pickle

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from getfilelistpy import getfilelist

from cmd_args_down_heic import CMDArgsDownHeic


def download_files(drive_service, path, heic_files):
	files_count = len(heic_files)
	for i, heic_file in enumerate(heic_files):
		file_id = heic_file['id']
		filename = heic_file['name']
		print('[{}/{}] id: {}'.format(i+1, files_count, file_id))
		print('[{}/{}] name: {}'.format(i+1, files_count, filename))

		request = drive_service.files().get_media(fileId=file_id)
		fh = io.FileIO(path + '/' + filename, 'wb')
		downloader = MediaIoBaseDownload(fh, request)
		done = False
		while done is False:
			status, done = downloader.next_chunk()
			print("download %d%%" % int(status.progress() * 100))


def compare_files_count(path, gdrive_files):
	filelist = glob.glob(path + '/*')
	download_files = set(map(lambda filename: filename.split('/')[-1], list(filter(lambda filename: len(filename) >= 5 and filename[-4:].lower() == 'heic', filelist))))
	failed_files = list(gdrive_files - download_files)
	for failed_file in failed_files:
		print('failed file: {}'.format(failed_file))


def main():
	SCOPES = ['https://www.googleapis.com/auth/drive']
	creds = None
	credFile = 'token.pickle'
	
	args_down_heic = CMDArgsDownHeic('cmd_args_down_heic', ['drive_id', 'path'])
	args = args_down_heic.values
	
	if os.path.exists(credFile):
		with open(credFile, 'rb') as token:
			creds = pickle.load(token)
	
	if not creds or not creds.valid:
		if creds and creds.expired and creds.refresh_token:
			creds.refresh(Request())
		else:
			flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
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

	heic_files = list(filter(lambda a_file: len(a_file['name']) >= 5 and a_file['name'][-4:].lower() == 'heic', res['fileList'][0]['files']))
	download_files(drive_service, args.path, heic_files)
	compare_files_count(args.path, set(map(lambda a_file: a_file['name'], heic_files)))


if __name__ == '__main__':
	main()
