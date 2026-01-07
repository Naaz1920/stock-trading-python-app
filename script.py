import requests
import os
import csv

from dotenv import load_dotenv
load_dotenv()

POLYGON_APY_KEY = os.getenv("Polygon_API_KEY")

print(POLYGON_APY_KEY)

LIMIT = 5

url = f'https://api.massive.com/v3/reference/tickers?market=stocks&active=true&order=asc&limit={LIMIT}&sort=ticker&apiKey={POLYGON_APY_KEY}'
response = requests.get(url)
tickers = []

data = response.json()
print(data.keys())

for ticker in data.get('results', []):
    tickers.append(ticker)

while 'next_url' in data:
    print('requesting next page', data['next_url'])
    response = requests.get(data['next_url'] + f'&apikey={POLYGON_APY_KEY}')
    data = response.json()
    print(data)
    for ticker in data.get('results', []):
        tickers.append(ticker)

print(f'Collected {len(tickers)} tickers')

example_ticker = {'ticker': 'AAEQ',
                  'name': 'Alpha Architect US Equity 2 ETF',
                  'market': 'stocks',
                  'locale': 'us',
                  'primary_exchange': 'XNAS',
                  'type': 'ETF',
                  'active': True,
                  'currency_name': 'usd',
                  'composite_figi': 'BBG01YY0GN44',
                  'share_class_figi': 'BBG01YY0GP12',
                  'last_updated_utc': '2026-01-06T07:06:31.407218507Z'}

# CSV field order matching example_ticker
fieldnames = [
    'ticker',
    'name',
    'market',
    'locale',
    'primary_exchange',
    'type',
    'active',
    'currency_name',
    'composite_figi',
    'share_class_figi',
    'last_updated_utc',
]

output_path = 'tickers.csv'
with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for t in tickers:
        row = {}
        for k in fieldnames:
            v = t.get(k, '')
            if isinstance(v, bool):
                v = str(v)
            row[k] = v
        writer.writerow(row)

print(f'Wrote {len(tickers)} rows to {output_path}')