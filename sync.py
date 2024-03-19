import os
import shutil
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from obsidian_api import ObsidianAPI  # Assuming there's an Obsidian API library available

# Define Google Drive API scopes
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

# Define Obsidian vault directory
VAULT_DIR = '/path/to/your/obsidian/vault'

# Function to authenticate with Google Drive API
def authenticate_google_drive():
    flow = InstalledAppFlow.from_client_secrets_file(
        'credentials.json', SCOPES)
    creds = flow.run_local_server(port=0)
    return creds

# Function to download files from Google Drive and move to Obsidian vault
def download_and_move_files(service, obsidian_api):
    # Fetch files from Google Drive
    results = service.files().list(
        q="mimeType='application/pdf'", fields="files(id, name)").execute()
    items = results.get('files', [])

    if not items:
        print('No PDF files found.')
    else:
        print('Downloading and moving PDF files:')
        for item in items:
            file_id = item['id']
            file_name = item['name']
            file_path = os.path.join(VAULT_DIR, file_name)

            # Download file from Google Drive
            request = service.files().get_media(fileId=file_id)
            fh = open(file_path, 'wb')
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
                print(f'Download {int(status.progress() * 100)}%.')
            
            # Move file to Obsidian vault
            shutil.move(file_path, VAULT_DIR)

            # Update Obsidian index
            obsidian_api.index_file(file_name, file_path)

        print('Download complete.')

def main():
    # Authenticate with Google Drive API
    creds = authenticate_google_drive()
    service = build('drive', 'v3', credentials=creds)

    # Initialize Obsidian API
    obsidian_api = ObsidianAPI()

    # Download and move files from Google Drive to Obsidian vault
    download_and_move_files(service, obsidian_api)

if __name__ == '__main__':
    main()
