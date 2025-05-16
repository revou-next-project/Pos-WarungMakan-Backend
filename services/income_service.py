from fastapi import HTTPException
from fastapi_sqlalchemy import db
from models.income_model import Income
from schemas.income_schema import CreateIncomeSchema
from datetime import datetime

from sqlalchemy import and_

from fastapi_sqlalchemy import db
from models.cashBalance_model import CashBalance, TransactionType
from fastapi import HTTPException
from datetime import datetime


async def create_income(income_data: CreateIncomeSchema, user_id: int):
    try:
        with db.session.begin():
            income = Income(
                amount      = income_data.amount,
                category    = income_data.category,
                descriptions = income_data.descriptions,
                date        = income_data.date or datetime.now()
            )
            cash_log = CashBalance(
                transaction_type = TransactionType.INCOME,
                amount           = income_data.amount,
                reference_id     = None,
                notes            = f"{income_data.category}: {income_data.descriptions}",
                recorded_by      = user_id
            )

            db.session.add_all([income, cash_log])

            db.session.flush()

            income.cash_log_id = cash_log.id

        return income
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
async def get_all_incomes(
        start_date: str,
        end_date: str
):
    try:
        query = db.session.query(Income)
        if start_date and end_date:
            query = query.filter(
                and_(Income.date >= start_date, Income.date < end_date)  
            )
            incomes = query.order_by(Income.date.desc()).all()
            data = [income.to_dict() for income in incomes]
            return {
                "total": len(data),
                "data": data
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
