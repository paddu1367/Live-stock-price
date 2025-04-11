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
sheet_title = "Sock Market Data"
spreadsheet = client.open(sheet_title).sheet1

# === Alpha Vantage Setup ===
API_KEY = os.environ["API_KEY"]
BASE_URL = "https://www.alphavantage.co/query"
FUNCTION = "TIME_SERIES_MONTHLY_ADJUSTED"

# === List of tickers ===
tickers = [
    "IBM", "AAPL", "GOOGL", "MSFT", "AMZN", "META", "TSLA", "NVDA", "NFLX", "ORCL",
    "INTC", "AMD", "SAP", "CRM", "CSCO", "ADBE", "QCOM", "TXN", "AVGO", "BA"
]

# === Pull & Upload Data for Each Ticker ===
for i, symbol in enumerate(tickers):
    print(f"📈 Fetching data for {symbol} ({i+1}/{len(tickers)})")

    params = {
        "function": FUNCTION,
        "symbol": symbol,
        "apikey": API_KEY
    }

    res = requests.get(BASE_URL, params=params)
    data = res.json()

    if "Monthly Adjusted Time Series" not in data:
        print(f"❌ Error fetching data for {symbol}: {data.get('Note', 'Unknown error')}")
        continue

    time_series = data["Monthly Adjusted Time Series"]
    rows = []

    for date in time_series.keys():
        d = time_series[date]
        rows.append([
            symbol,
            date,
            d["1. open"],
            d["2. high"],
            d["3. low"],
            d["4. close"],
            d["5. adjusted close"],
            d["6. volume"]
        ])

    # === Upload data ===
    spreadsheet.append_rows(rows)

    print(f"✅ Uploaded {len(rows)-1} rows for {symbol}")

    # === Respect API Rate Limit (5 calls/minute) ===
    if i < len(tickers) - 1:
        print("⏱ Waiting 12 seconds to avoid rate limits...")
        time.sleep(12)

print("🎉 All tickers uploaded successfully!")
