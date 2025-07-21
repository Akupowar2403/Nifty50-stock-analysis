# # app/models.py
# from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, UniqueConstraint, DateTime
# from sqlalchemy.orm import relationship # Used for defining relationships between models
# from app.database import Base # Assuming this is your Base from database.py

# class Stock(Base):
#     __tablename__ = "stocks"

#     id = Column(Integer, primary_key=True, index=True)
#     symbol = Column(String, unique=True, index=True, nullable=False)
#     company_name = Column(String, nullable=True) # Can be null if not fetched
#     latest_price = Column(Float, nullable=True) # Store latest closing price
#     last_updated = Column(DateTime, nullable=True) # Timestamp of last fetch

#     # Relationship to DailyData: A stock has many daily data entries
#     # lazy='raise' is often good for development to catch N+1 issues
#     daily_data = relationship("DailyData", back_populates="stock", lazy="selectin")

# class DailyData(Base):
#     __tablename__ = "daily_data"  

#     id = Column(Integer, primary_key=True, index=True)
#     stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=False)
#     date = Column(Date, index=True, nullable=False)
#     open_price = Column(Float, nullable=False)
#     high_price = Column(Float, nullable=False)
#     low_price = Column(Float, nullable=False)
#     close_price = Column(Float, nullable=False)
#     volume = Column(Integer, nullable=False)

#     # Calculated Technical Indicators (store them to avoid re-calculation)
#     sma_20 = Column(Float, nullable=True) # Nullable because first 19 days won't have SMA
#     daily_return = Column(Float, nullable=True) # Nullable for the very first day

#     # Composite Unique Constraint: Ensure only one entry per stock per day
#     __table_args__ = (UniqueConstraint("stock_id", "date", name="_stock_date_uc"),)

#     # Relationship to Stock: A daily data entry belongs to one stock
#     stock = relationship("Stock", back_populates="daily_data")

from sqlalchemy import Column, Integer, Float, String, Date, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Stock(Base):
    __tablename__ = "stocks"
    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String, unique=True, index=True)
    company_name = Column(String)
    latest_price = Column(Float)
    last_updated = Column(Date)
    data = relationship("DailyData", back_populates="stock")

class DailyData(Base):
    __tablename__ = "dailydata"
    id = Column(Integer, primary_key=True, autoincrement=True)
    stock_id = Column(Integer, ForeignKey("stocks.id"))
    date = Column(Date)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(Integer)
    sma_20 = Column(Float)
    daily_return = Column(Float)
    __table_args__ = (UniqueConstraint("stock_id", "date", name="_stock_date_uc"),)
    stock = relationship("Stock", back_populates="data")
