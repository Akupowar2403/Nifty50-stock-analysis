Nifty50 Historical Stock Analysis API

Author: Akanksha Shivaji Powar
Email: powarakanksha1@gmail.com
Submission Date: July 21, 2025

🚩 Quick Start: Interactive API Docs
Access the Swagger UI to try endpoints directly:
http://127.0.0.1:8000/docs

Overview
This backend project offers a FastAPI-powered REST API to fetch, store, and analyze historical stock data for India's NIFTY 50 index using Yahoo Finance data.
All historical data is stored in a local SQLite database and processed via SQLAlchemy, enabling robust storage and efficient technical analysis.

Features
Automated Data Fetching: Loads 3 months of daily prices for NIFTY 50 stocks via yfinance.

Persistent Storage: Stores all prices and indicators in SQLite using an efficient, normalized schema.

Technical Indicators: Calculates 20-day Simple Moving Average (SMA), daily percent returns, and volume analysis.

REST API: Clean endpoints for listing, price history, and indicator-driven stock analysis.

Validated Data: Uses Pydantic models to ensure safe API contracts and database integrity.

Auto Data Cleaning: Includes automatic repair of database entries with missing company names.

Interactive Documentation: Built-in Swagger and ReDoc API docs.

Setup Instructions
1. Clone the Repository
bash
git clone https://github.com/Akupowar2403/Nifty50-stock-analysis.git
cd Nifty50-stock-analysis
2. Create & Activate Virtual Environment
bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
3. Install Dependencies
bash
pip install -r requirements.txt
4. Run the Application
bash
uvicorn app.main:app --reload
The API will be available at http://127.0.0.1:8000/.

API Documentation
Interactive Swagger UI:
http://127.0.0.1:8000/docs

Alternative docs (ReDoc):
http://127.0.0.1:8000/redoc

Key Endpoints
Method	Endpoint	Description
POST	/stocks/fetch-historical	Fetch & store 3 months of data for all tracked NIFTY stocks.
GET	/stocks	List all tracked stocks with latest price and info.
GET	/stocks/{symbol}/history	Get full price/indicator history for a stock.
GET	/stocks/{symbol}/analysis	Get indicator analysis for a single stock.
Example Usage
Fetch and store data:

bash
curl -X POST http://127.0.0.1:8000/stocks/fetch-historical
Get all stocks:

bash
curl http://127.0.0.1:8000/stocks
Database Schema
Table: stocks
Column	Type	Description
id	int	Primary key
symbol	str	Stock symbol (unique)
company_name	str	Company name
latest_price	float	Latest closing price
last_updated	date	Date of last data update
Table: dailydata
Column	Type	Description
id	int	Primary key
stock_id	int	Foreign key to stocks.id
date	date	Date for daily data
open	float	Open price
high	float	High price
low	float	Low price
close	float	Close price
volume	int	Trading volume
sma_20	float	20-day SMA
daily_return	float	Daily percent return
Schema is created automatically on server startup.

Example API Responses
GET /stocks
json
[
  {
    "symbol": "RELIANCE.NS",
    "company_name": "Reliance Industries",
    "latest_price": 2468.5,
    "last_updated": "2025-07-21"
  }
]
GET /stocks/RELIANCE.NS/analysis
json
{
  "symbol": "RELIANCE.NS",
  "price": 2468.5,
  "sma_20": 2455.1,
  "above_sma": true,
  "trend": "Uptrend",
  "volume_analysis": "Normal",
  "volatility": 1.45
}
Error Handling & Troubleshooting
500 Internal Server Error / ValidationError:
All company_name fields must be set. If you see this, run the provided SQL patch or fetch endpoint again.

404 Not Found:
Double-check the URL and HTTP method (GET/POST).

422 Validation Error:
Make sure to send all required parameters in your request.

Design Decisions & Assumptions
Only stocks in the NIFTY 50 list are tracked.

All technical indicators are calculated for stored data, not in real time.

Data schema is designed for extensibility, validation, and rapid analysis.

Dependencies
fastapi

uvicorn

sqlalchemy

yfinance

pandas

pydantic

numpy

See requirements.txt for the full list and versions.

Maintenance & Reset
To reset or reinitialize the database:

Delete stocks.db in your project folder.

Restart the server and call the fetch endpoint to repopulate.

Contact
For questions or support, email:
Akanksha Shivaji Powar
powarakanksha1@gmail.com

Submission Date: July 21, 2025

