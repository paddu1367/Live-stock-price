import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
import os
from datetime import datetime

# Load creds from environment
creds_dict = json.loads(os.environ["GOOGLE_CREDS_JSON"])
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

sheet = client.open("Your Google Sheet Name").sheet1
now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
sheet.append_row(["Updated from GitHub Action at", now])
