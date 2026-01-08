import requests
import os
import snowflake.connector
from datetime import datetime

from dotenv import load_dotenv
load_dotenv()

POLYGON_API_KEY = os.getenv("Polygon_API_KEY")  # Fixed typo from POLYGON_APY_KEY

print(POLYGON_API_KEY)

LIMIT = 5

def run_stock_job():
    url = f'https://api.polygon.io/v3/reference/tickers?market=stocks&active=true&order=asc&limit={LIMIT}&sort=ticker&apiKey={POLYGON_API_KEY}'  # Fixed API URL from 'api.massive.com' to 'api.polygon.io'
    response = requests.get(url)
    tickers = []

    data = response.json()
    print(data.keys())

    for ticker in data.get('results', []):
        tickers.append(ticker)

    while 'next_url' in data:
        print('requesting next page', data['next_url'])
        response = requests.get(data['next_url'] + f'&apikey={POLYGON_API_KEY}')
        data = response.json()
        print(data)
        for ticker in data.get('results', []):
            tickers.append(ticker)

    print(f'Collected {len(tickers)} tickers')

    # Snowflake connection details from environment variables
    account = os.getenv("SNOWFLAKE_ACCOUNT")
    user = os.getenv("SNOWFLAKE_USER")
    password = os.getenv("SNOWFLAKE_PASSWORD")
    warehouse = os.getenv("SNOWFLAKE_WAREHOUSE")
    database = os.getenv("SNOWFLAKE_DATABASE")
    schema = os.getenv("SNOWFLAKE_SCHEMA")
    role = os.getenv("SNOWFLAKE_ROLE")
    table_name = os.getenv("SNOWFLAKE_TABLE", "stock_tickers")  # Default to 'tickers' if not set

    # Connect to Snowflake
    conn = snowflake.connector.connect(
        account=account,
        user=user,
        password=password,
        warehouse=warehouse,
        database=database,
        schema=schema,
        role=role
    )
    cursor = conn.cursor()

    # Create table if it doesn't exist
    create_table_query = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        ticker VARCHAR,
        name VARCHAR,
        market VARCHAR,
        locale VARCHAR,
        primary_exchange VARCHAR,
        type VARCHAR,
        active BOOLEAN,
        currency_name VARCHAR,
        composite_figi VARCHAR,
        share_class_figi VARCHAR,
        last_updated_utc TIMESTAMP,  -- Stored as string; can be parsed to TIMESTAMP if needed
        ds TIMESTAMP
    )
    """
    cursor.execute(create_table_query)

    # Prepare data for insertion
    insert_query = f"""
    INSERT INTO {table_name} (ticker, name, market, locale, primary_exchange, type, active, currency_name, composite_figi, share_class_figi, last_updated_utc, ds)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    data_to_insert = []
    for t in tickers:
        row = (
            t.get('ticker', ''),
            t.get('name', ''),
            t.get('market', ''),
            t.get('locale', ''),
            t.get('primary_exchange', ''),
            t.get('type', ''),
            t.get('active', False),
            t.get('currency_name', ''),
            t.get('composite_figi', ''),
            t.get('share_class_figi', ''),
            t.get('last_updated_utc', ''),
            datetime.utcnow().strftime('%Y-%m-%d')
        )
        data_to_insert.append(row)

    # Insert data
    cursor.executemany(insert_query, data_to_insert)
    conn.commit()

    print(f'Inserted {len(tickers)} rows into Snowflake table {table_name}')

    # Close connection
    cursor.close()
    conn.close()

if __name__ == '__main__':  # Fixed from '_main_'
    run_stock_job()