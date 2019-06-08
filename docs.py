#!/usr/bin/python3

import os.path, pickle, zipfile

from apiclient.http import MediaIoBaseDownload
from apiclient.http import MediaIoBaseUpload
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from io import BytesIO

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive']

#Creates Service object to allow interaction with Google Drive
def get_service():
	"""Shows basic usage of the Drive v3 API.
	Prints the names and ids of the first 10 files the user has access to.
	"""
	creds = None
	# The file token.pickle stores the user's access and refresh tokens, and is
	# created automatically when the authorization flow completes for the first
	# time.
	if os.path.exists('token.pickle'):
		with open('token.pickle', 'rb') as token:
			creds = pickle.load(token)
	# If there are no (valid) credentials available, let the user log in.
	if not creds or not creds.valid:
		if creds and creds.expired and creds.refresh_token:
			creds.refresh(Request())
		else:
			flow = InstalledAppFlow.from_client_secrets_file(
				'credentials.json', SCOPES)
			creds = flow.run_local_server()
		# Save the credentials for the next run
		with open('token.pickle', 'wb') as token:
			pickle.dump(creds, token)

	service = build('drive', 'v3', credentials=creds)
	return service

#Creates a folder and returns its ID
def create_folder(service, file_path):
	folder_metadata = {
	'name': file_path,
	'mimeType': 'application/vnd.google-apps.folder'
	}
	folder = service.files().create(body=folder_metadata, fields= 'id').execute()

	#print('Folder created, ID: %s' % folder.get('id'))
	return folder.get('id')

#Stores a file into a folder
def store_doc(service, folderId, file_name, file_path):
	file_metadata = {
	'name': file_name,
	'mimeType': 'application/vnd.google-apps.document',
	'parents': [folderId]
	}
	media = MediaIoBaseUpload(file_path, mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
	file = service.files().create(body=file_metadata,
									media_body=media,
									fields = 'id').execute()

	print('File created, ID: %s' % file.get('id'))

#Returns folder id and service object for document insertion into the folder
def begin_storage(file_path):
	service = get_service()
	folderId = create_folder(service, file_path)
	return service, folderId

#Lists folders and their IDs (excluding folders in Trash)
def list_files(service):
	results = service.files().list(q="(mimeType='application/vnd.google-apps.folder') and (trashed=False)", fields="nextPageToken, files(id, name)").execute()
	folders = results.get('files', [])

	print('Folder List')
	for folder in folders:
		print(folder.get('name') + ' (ID: ' +folder.get('id') + ')')

# Returns a list of files in a folder with the given ID
def get_files_list_from_folder(service, folderId):
	query = "'" +folderId + "' in parents"
	page_token = None
	files = list()
	while True:
		param = {}

		if page_token:
			param['pageToken'] = page_token

		results = service.files().list(q=query, fields='nextPageToken, files(id, name)', **param).execute()
		files += results.get('files', []) #grabs all of the files from the folder

		page_token = results.get('nextPageToken')
		if not page_token:
			break
	return files

# Returns the bytes from an image in a document
def get_image_bytes_from_doc(service, file):
	# Download file to memory
	request = service.files().export_media(fileId=file['id'], mimeType='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
	fh = BytesIO()
	downloader = MediaIoBaseDownload(fh, request)
	done = False
	while done is False:
		status, done = downloader.next_chunk()

	# Extract image from file and return the image's bytes
	zipRef = zipfile.ZipFile(fh, 'r')
	imgBytes = zipRef.read('word/media/image1.png')
	zipRef.close()
	return BytesIO(imgBytes)
