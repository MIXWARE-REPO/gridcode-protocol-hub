from __future__ import annotations
import io
from pathlib import Path
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

TOKEN = Path('/home/laia/.hermes/google_token.json')
SCOPES = ['https://www.googleapis.com/auth/drive']
creds = Credentials.from_authorized_user_file(str(TOKEN), SCOPES)
if creds.expired and creds.refresh_token:
    creds.refresh(Request())
    TOKEN.write_text(creds.to_json(), encoding='utf-8')

service = build('drive', 'v3', credentials=creds, cache_discovery=False)

BASE_DIR = Path('/home/laia/gridcode-protocol-hub/gridcode-source-base')
BASE_DIR.mkdir(parents=True, exist_ok=True)

FILES = [
    ('1krT4XXgHCOgJc-Ya-FOYyd9eG-ihF_Ye', 'gridcode-a4-paginado-liviano-no-float-brand-reforzado.html', 'text/html'),
    ('1ZeOrdlkRpoR6ov7wVgVTBxYecMy0PEZa', 'logo.png', 'image/png'),
]

for file_id, name, mime in FILES:
    req = service.files().get_media(fileId=file_id, supportsAllDrives=True)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, req)
    done = False
    while not done:
        _, done = downloader.next_chunk()
    data = fh.getvalue()
    out = BASE_DIR / name
    out.write_bytes(data)
    print(str(out))
