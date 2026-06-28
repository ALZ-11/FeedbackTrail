import os
import io
import pandas as pd
from dotenv import load_dotenv
import googleapiclient.discovery
import googleapiclient.http
from google.oauth2 import service_account

load_dotenv()

def fetch_data_from_drive():
    """
    Authenticates with Google Drive and downloads the CSV database
    directly into a Pandas DataFrame without saving a local copy.
    """
    print("Authenticating with Google Drive API...")
    credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "credentials.json")
    file_id = os.getenv("GOOGLE_DRIVE_FILE_ID")

    if not credentials_path or not os.path.exists(credentials_path):
        raise FileNotFoundError(f"Credentials file not found at: {credentials_path}")
    if not file_id:
        raise ValueError("GOOGLE_DRIVE_FILE_ID is not set in your .env file.")

    # Authenticate using service account credentials
    credentials = service_account.Credentials.from_service_account_file(credentials_path)
    drive_service = googleapiclient.discovery.build('drive', 'v3', credentials=credentials)

    print(f"Downloading database CSV (File ID: {file_id})...")
    request = drive_service.files().get_media(fileId=file_id)
    
    # In-memory download stream
    file_io = io.BytesIO()
    downloader = googleapiclient.http.MediaIoBaseDownload(file_io, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()
        
    file_io.seek(0)
    print("Download complete.")
    
    # Load stream directly into a Pandas DataFrame
    df = pd.read_csv(file_io, encoding="utf-8")
    return df

def main():
    try:
        df = fetch_data_from_drive()
        
        # validation
        print("\n" + "="*50)
        print("DATABASE VALIDATION SUCCESSFUL")
        print("="*50)
        print(f"Dataset Shape: {df.shape[0]} rows, {df.shape[1]} columns")
        print("\nDatabase Schema and Data Types:")
        print(df.dtypes)
        print("\nFirst 5 Rows of the Dataset:")
        print(df.head())
        print("="*50 + "\n")
        
    except Exception as e:
        print(f"\n[ERROR] An error occurred while fetching the data: {e}\n")

if __name__ == "__main__":
    main()