#!../../bin/python3

import os.path
import pickle

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from getfilelistpy import getfilelist

from cmd_args_drive_mon import CMDArgsDriveMon


def main():
	SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly']
	creds = None
	credFile = 'token.pickle'
	
	args_drive_mon = CMDArgsDriveMon('cmd_args_drive_mon', ['drive_id'])
	args = args_drive_mon.values
	
	if os.path.exists(credFile):
		with open(credFile, 'rb') as token:
			creds = pickle.load(token)
	
	if not creds or not creds.valid:
		if creds and creds.expired and creds.refresh_token:
			creds.refresh(Request())
		else:
			flow = InstalledAppFlow.from_client_secrets_file('../../config/credentials.json', SCOPES)
			creds = flow.run_local_server()
		with open(credFile, 'wb') as token:
			pickle.dump(creds, token)
	
	resource = {
		"oauth2": creds,
		"id": args.drive_id,
		"fields": "files(name, id)",
	}
	
	res = getfilelist.GetFileList(resource)
	print(res)


if __name__ == '__main__':
	main()
