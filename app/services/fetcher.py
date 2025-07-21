import yfinance as yf
import pandas as pd
from sqlalchemy.orm import Session
from datetime import date, timedelta, datetime
from app.models import Stock, DailyData
from app.constants import NIFTY_STOCKS  # This is a list of dicts (symbol, company_name)

# Correct mapping for NIFTY_STOCKS as list of dicts!
SYMBOL_TO_COMPANY = {s["symbol"]: s["company_name"] for s in NIFTY_STOCKS}

# ---- PATCH: Fix old stocks with null or blank company_name ----
def fix_null_company_names(db):
    from app.constants import NIFTY_STOCKS
    symbol_to_company = {s["symbol"]: s["company_name"] for s in NIFTY_STOCKS}
    from app.models import Stock
    print("Fixing company_name for old stocks...")
    updated = False
    for stock in db.query(Stock).all():
        if not stock.company_name or str(stock.company_name).strip() == "":
            stock.company_name = symbol_to_company.get(stock.symbol, stock.symbol)
            updated = True
    if updated:
        db.commit()
        print("Patched null company_name values in database.")
    else:
        print("No missing company_name values found.")


def fetch_and_store_data(db: Session):
    fix_null_company_names(db)  # Patch DB on every fetch run (safe for dev & prod)
    print("Starting historical data fetch and storage...")
    for symbol in SYMBOL_TO_COMPANY:
        company_name = SYMBOL_TO_COMPANY[symbol]
        print(f"Processing stock: {symbol}")
        try:
            # 1. Get or Create Stock entry
            stock_obj = db.query(Stock).filter(Stock.symbol == symbol).first()
            if not stock_obj:
                print(f"Creating new stock entry for {symbol}")
                stock_obj = Stock(symbol=symbol, company_name=company_name)
                db.add(stock_obj)
                db.commit()
                db.refresh(stock_obj)
            # Patch if name is missing in case of legacy row
            elif not stock_obj.company_name or not stock_obj.company_name.strip():
                stock_obj.company_name = company_name
                db.add(stock_obj)
                db.commit()
                db.refresh(stock_obj)

            # 2. Determine the start date for yfinance download
            latest_db_date = db.query(DailyData.date) \
                .filter(DailyData.stock_id == stock_obj.id) \
                .order_by(DailyData.date.desc()) \
                .first()
            start_date_yf = date.today() - timedelta(days=90)
            if latest_db_date:
                start_date_yf = latest_db_date[0] + timedelta(days=1)
            if start_date_yf >= date.today():
                print(f"No new historical data needed for {symbol}. Database is up-to-date or ahead.")
                continue

            # 3. Fetch data from yfinance
            print(f"Fetching from {start_date_yf} to {date.today()} for {symbol}")
            df = yf.download(symbol, start=start_date_yf, end=date.today(), interval="1d")

            if df.empty:
                print(f"No data found for {symbol} for the period {start_date_yf} to {date.today()}.")
                continue

            # Flatten MultiIndex and lowercase columns
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = [
                    '_'.join([str(level) for level in col if level])
                    for col in df.columns.values
                ]
            df.columns = [str(col).lower() for col in df.columns]
            print(f"Columns for {symbol}: {df.columns.tolist()}")

            # Handle columns ending with the symbol (e.g., 'open_reliance.ns')
            suffix = f"_{symbol.lower()}"
            column_map = {
                'open' + suffix: 'open',
                'high' + suffix: 'high',
                'low' + suffix: 'low',
                'close' + suffix: 'close',
                'adj close' + suffix: 'adj_close',
                'volume' + suffix: 'volume'
            }
            selected_cols = {orig: new for orig, new in column_map.items() if orig in df.columns}
            df = df[list(selected_cols.keys())]
            df = df.rename(columns=selected_cols)

            if 'close' not in df.columns and 'adj_close' in df.columns:
                df['close'] = df['adj_close']

            print(f"Renamed for model for {symbol}: {df.columns.tolist()}")

            # 4. Calculate Technical Indicators
            df['sma_20'] = df['close'].rolling(window=20).mean()
            df['daily_return'] = df['close'].pct_change() * 100

            new_daily_entries = []
            for index, row in df.iterrows():
                entry_date = index.date() if hasattr(index, 'date') else index
                if entry_date <= date.today():
                    daily_data_entry = DailyData(
                        stock_id=stock_obj.id,
                        date=entry_date,
                        open=row.open,
                        high=row.high,
                        low=row.low,
                        close=row.close,
                        volume=row.volume,
                        sma_20=row.sma_20 if pd.notna(row.sma_20) else None,
                        daily_return=row.daily_return if pd.notna(row.daily_return) else None
                    )
                    new_daily_entries.append(daily_data_entry)

            if new_daily_entries:
                db.add_all(new_daily_entries)
                db.commit()
                print(f"Successfully added {len(new_daily_entries)} new daily entries for {symbol}.")
            else:
                print(f"No new daily entries to add for {symbol}.")

            # 6. Update Stock's latest price and last updated
            if not df.empty:
                stock_obj.latest_price = df['close'].iloc[-1]
                stock_obj.last_updated = datetime.now()
                db.add(stock_obj)
                db.commit()
                print(f"Updated latest price and last updated time for {symbol}.")

        except Exception as e:
            print(f"Error processing {symbol}: {e}")
            db.rollback()
    print("Historical data fetch and storage completed.")


