from __future__ import annotations
import json
from pathlib import Path
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

TOKEN = Path('/home/laia/.hermes/google_token.json')
SCOPES = ['https://www.googleapis.com/auth/drive']
creds = Credentials.from_authorized_user_file(str(TOKEN), SCOPES)
if creds.expired and creds.refresh_token:
    creds.refresh(Request())
    TOKEN.write_text(creds.to_json(), encoding='utf-8')

service = build('drive', 'v3', credentials=creds, cache_discovery=False)

def search(q, max_items=20):
    res = service.files().list(
        q=q,
        corpora='allDrives',
        includeItemsFromAllDrives=True,
        supportsAllDrives=True,
        pageSize=max_items,
        fields='files(id,name,mimeType,modifiedTime,webViewLink,parents,shortcutDetails)',
    ).execute()
    return res.get('files', [])

queries = [
    "name contains 'gridcode-a4-paginado-liviano-no-float-brand-reforzado.html' and trashed = false",
    "name contains 'gridcode-a4-paginado-liviano' and trashed = false",
    "name contains 'brand-reforzado' and trashed = false",
    "name contains 'logo.png' and trashed = false",
    "name contains 'gridcode' and mimeType contains 'html' and trashed = false",
]

for q in queries:
    print('QUERY:', q)
    files = search(q)
    print(json.dumps(files, indent=2, ensure_ascii=False))
    print('---')
