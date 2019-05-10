import os
import pickle
from io import BytesIO, StringIO
import pandas as pd
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


class Drive:
    """
    Drive Object connects nd retrieves data from Google Drive.
    Initialize with local path containing Google Credentials file and the FolderID for the google drive folder.
    Contains two methods: list_files and get_files.
    """
    def __init__(self, path:str, folder_id:str):

        self.folder_id = folder_id
        self.cred_file = os.path.join(path, 'credentials.json')
        self.token_file = os.path.join(path, 'token.pickle')

        self.SCOPES = ['https://www.googleapis.com/auth/drive']

        self.creds = None
        self.service = self.authorize()

    def open_pickle(self):
        with open(self.token_file, 'rb') as token:
            file = pickle.load(token)
        return file

    def save_pickle(self, file):
        with open(self.token_file, 'wb') as token:
            pickle.dump(file, token)

    def authorize(self):
        """Authorizes Google Connection and creates a credentials object to apss to commands"""
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists(self.token_file):
            self.creds = self.open_pickle()
        # If there are no (valid) credentials available, let the user log in.
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(self.cred_file, self.SCOPES)
                self.creds = flow.run_local_server()
            # Save the credentials for the next run
            self.save_pickle(self.creds)

        return build('drive', 'v3', credentials=self.creds)

    def list_files(self):
        """Creates a dictionary with name: id """

        output = []
        nextPageToken = None
        while True:
            response = self.service.files().list(q=f"parents in '{self.folder_id}'", pageSize=100,
                                            pageToken=nextPageToken).execute()
            for file in response.get('files', []):
                output.append((file.get('name'), file.get('id')))
            if 'nextPageToken' not in response:
                break
            else:
                nextPageToken = response['nextPageToken']

        return dict(output)

    def get_file(self, file_id):
        """Receives fileID and returns a the file as a pandas dataframe"""
        request = self.service.files().get_media(fileId=file_id)
        fh = BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print("Download %d%%." % int(status.progress() * 100), file_id)
        return pd.read_csv(StringIO(fh.getvalue().decode()))

