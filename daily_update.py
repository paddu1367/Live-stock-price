import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
import os
import time

# === Setup Google Sheets ===
creds_dict = json.loads(os.environ["GOOGLE_CREDS_JSON"])  # Or load from file
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

# Open or create the spreadsheet
sheet_title = "live stock"
spreadsheet = client.open(sheet_title).sheet1
INTERVAL = '5min'

# === Alpha Vantage Setup ===
API_KEY = os.environ["API_KEY"]
BASE_URL = "https://www.alphavantage.co/query"
FUNCTION = "TIME_SERIES_INTRADAY"

# === List of tickers ===
tickers = [
    "IBM", "AAPL", "GOOGL", "MSFT", "AMZN", "META", "TSLA", "NVDA", "NFLX", "ORCL",
    "INTC", "AMD", "SAP", "CRM", "CSCO", "ADBE", "QCOM", "TXN", "AVGO", "BA"
]
rows = [["Equity","Date", "Open", "High", "Low", "Close", "Adjusted Close", "Volume"]]
# === Pull & Upload Data for Each Ticker ===
for i, symbol in enumerate(tickers):
    print(f"📈 Fetching data for {symbol} ({i+1}/{len(tickers)})")

    params = {
        "function": FUNCTION,
        "symbol": symbol,
        "interval": INTERVAL,
        "&outputsize":"full",
        "apikey": API_KEY
    }

    res = requests.get(BASE_URL, params=params)
    data = res.json()

    # === Parse the data ===
    time_series_key = f'Time Series ({INTERVAL})'
    

    if time_series_key in data:
        for timestamp, values in data[time_series_key].items():
            rows.append([
            symbol,
            timestamp,
            values["1. open"],
            values["2. high"],
            values["3. low"],
            values["4. close"],
            values["5. volume"]
        ])
    else:
        print("Error: No time series found.")
        print(data)

    # === Upload data ===
    spreadsheet.append_rows(rows)
    rows = []
    print(f"✅ Uploaded {len(rows)-1} rows for {symbol}")

    # === Respect API Rate Limit (5 calls/minute) ===
    if i < len(tickers) - 1:
        print("⏱ Waiting 12 seconds to avoid rate limits...")
        time.sleep(12)

print("🎉 All tickers uploaded successfully!")
