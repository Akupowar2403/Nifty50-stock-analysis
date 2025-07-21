from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import traceback

from app.database import SessionLocal, engine
from app import models, crud
from app.schemas import StockBase, DailyDataOut, StockAnalysis
from app.services.fetcher import fetch_and_store_data

# Ensure all tables are created at app startup
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Nifty50 Historical Stock Analysis API",
    description="Backend service to analyze and compare NIFTY 50 stock performance.",
    version="1.0.0"
)

def get_db():
    """Dependency for getting a DB session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", tags=["Health"])
def root():
    """API health/status endpoint."""
    return {"message": "Welcome to the Stock Analysis API!"}

@app.post("/stocks/fetch-historical", status_code=status.HTTP_201_CREATED, tags=["Data Ingestion"])
def fetch_stocks(db: Session = Depends(get_db)):
    """
    Fetch and store the last 3 months of historical data for all tracked NIFTY stocks.
    """
    try:
        fetch_and_store_data(db)
        return {"message": "Historical stock data fetched and stored successfully."}
    except Exception as e:
        print("Full traceback error:")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching stock data: {str(e)}"
        )

@app.get("/stocks", response_model=List[StockBase], tags=["Stocks"])
def list_stocks(db: Session = Depends(get_db)):
    """
    List all tracked stocks with their latest price and meta info.
    """
    stocks = crud.get_all_stocks(db)
    if not stocks:
        raise HTTPException(status_code=404, detail="No stocks found.")
    return stocks

@app.get("/stocks/{symbol}/history", response_model=List[DailyDataOut], tags=["Stocks"])
def stock_history(symbol: str, db: Session = Depends(get_db)):
    """
    Retrieve historical daily data (OHLCV + indicators) for a specific stock.
    """
    data = crud.get_stock_history(db, symbol)
    if not data:
        raise HTTPException(status_code=404, detail=f"Stock '{symbol}' not found.")
    return data

@app.get("/stocks/{symbol}/analysis", response_model=StockAnalysis, tags=["Stocks"])
def stock_analysis(symbol: str, db: Session = Depends(get_db)):
    """
    Provides a comprehensive analysis report for a specific stock
    (including SMA, price trend, volume analysis, and volatility).
    """
    analysis = crud.get_stock_analysis(db, symbol)
    if analysis is None:
        raise HTTPException(status_code=404, detail=f"Stock '{symbol}' not found or insufficient data for analysis.")
    return analysis

# (TODO) ADD /analysis/performance endpoint as required by the assignment.
