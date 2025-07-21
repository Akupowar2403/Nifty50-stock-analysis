from typing import List, Optional
from datetime import date
from pydantic import BaseModel

# --- Schema for /stocks and GET all stocks ---
class StockBase(BaseModel):
    symbol: str
    company_name: str
    latest_price: Optional[float] = None  # Might be not available if not updated yet
    last_updated: Optional[date] = None

# --- Schema for a single day's data (history) ---
class DailyDataOut(BaseModel):
    date: date
    open: float
    high: float
    low: float
    close: float
    volume: int
    sma_20: Optional[float] = None
    daily_return: Optional[float] = None

# --- Schema for /stocks/{symbol}/analysis ---
class StockAnalysis(BaseModel):
    symbol: str
    price: float
    sma_20: Optional[float]
    above_sma: Optional[bool]
    trend: Optional[str]
    volume_analysis: Optional[str]
    volatility: Optional[float]
