from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from apiclient import errors
from apiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive']

#DEV FUNCTION TO DELETE FOLDER(S)#
def del_folder(id):
    service.files().delete(fileId=id).execute()

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

    #GRABS FIRST 10 ITEMS#
    # Call the Drive v3 API
    #results = service.files().list(
    #    pageSize=10, fields="nextPageToken, files(id, name)").execute()
    #items = results.get('files', [])
    

    #LISTS ITEMS#
    #if not items:
    #    print('No files found.')
    #else:
    #    print('Files:')
    #    for item in items:
    #        print(u'{0} ({1})'.format(item['name'], item['id']))
	    #Deletes things
            #service.files().delete(fileId=item['id']).execute()

#Creates a folder and returns its ID
def create_folder(service, file_path):
    folder_metadata = {
    'name': file_path,
    'mimeType': 'application/vnd.google-apps.folder'
    }
    folder = service.files().create(body=folder_metadata, fields= 'id').execute()

    print('Folder created, ID: %s' % folder.get('id'))
    return folder.get('id')

#Stores a file into a folder
def store_doc(service, folderId, file_path):
    file_metadata = {
    'name': file_path,
    'mimeType': 'application/vnd.google-apps.document',
    'parents': [folderId]
    }
    media = MediaFileUpload(file_path, mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
    file = service.files().create(body=file_metadata,
                                  media_body=media,
                                  fields = 'id').execute()
    
    print('File created, ID: %s' % file.get('id'))

#Returns folder id and service object for document insertion into the folder
def begin_storage(file_path):
    service = get_service()
    folderId = create_folder(service, file_path)
    return service, folderId
    

if __name__ == '__main__':
    service, folderId = begin_storage('example/path')
    store_doc(service, folderId, 'testdoc1.docx')
    store_doc(service, folderId, 'testdoc2.docx')
    store_doc(service, folderId, 'testdoc3.docx')