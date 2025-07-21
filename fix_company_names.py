from app.database import SessionLocal
from app.models import Stock
from app.constants import NIFTY_STOCKS
from app.database import SessionLocal, engine
from app import models

models.Base.metadata.create_all(bind=engine)

SYMBOL_TO_COMPANY = {s["symbol"]: s["company_name"] for s in NIFTY_STOCKS}

def fix_null_company_names():
    db = SessionLocal()
    updated = False
    for stock in db.query(Stock).all():
        if not stock.company_name or not str(stock.company_name).strip():
            print(f"Patching {stock.symbol}: company_name was '{stock.company_name}'")
            stock.company_name = SYMBOL_TO_COMPANY.get(stock.symbol, stock.symbol)
            updated = True
    if updated:
        db.commit()
        print("Patched all null/blank company_name values in database.")
    else:
        print("No missing company_name values found.")
    db.close()

if __name__ == "__main__":
    fix_null_company_names()
