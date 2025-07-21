from app import models
import numpy as np

def get_all_stocks(db):
    return db.query(models.Stock).all()

def get_stock_history(db, symbol):
    stock = db.query(models.Stock).filter(models.Stock.symbol == symbol).first()
    if not stock:
        return []
    return (
        db.query(models.DailyData)
        .filter(models.DailyData.stock_id == stock.id)
        .order_by(models.DailyData.date)
        .all()
    )

def get_stock_analysis(db, symbol):
    stock = db.query(models.Stock).filter(models.Stock.symbol == symbol).first()
    if not stock:
        return None

    daily_data = (
        db.query(models.DailyData)
        .filter(models.DailyData.stock_id == stock.id)
        .order_by(models.DailyData.date.desc())
        .limit(21)
        .all()
    )
    if len(daily_data) < 2:
        return None

    closes = [day.close for day in reversed(daily_data)]
    volumes = [day.volume for day in reversed(daily_data)]

    sma_20 = sum(closes[-20:]) / 20 if len(closes) >= 20 else None
    above_sma = closes[-1] > sma_20 if sma_20 is not None else None

    returns = [(closes[i] - closes[i-1]) / closes[i-1] * 100 for i in range(1, len(closes))]
    volatility = float(np.std(returns)) if returns else None

    avg_volume = sum(volumes[-20:]) / len(volumes[-20:]) if len(volumes) >= 20 else None
    volume_analysis = (
        "Unusually high" if avg_volume and volumes[-1] > avg_volume * 1.5 else "Normal"
    )

    trend = (
        "Uptrend" if len(returns) >= 5 and all(r > 0 for r in returns[-5:]) else "Downtrend"
    )

    return {
        "symbol": symbol,
        "price": closes[-1],
        "sma_20": sma_20,
        "above_sma": above_sma,
        "trend": trend,
        "volume_analysis": volume_analysis,
        "volatility": volatility,
    }
