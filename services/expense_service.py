from fastapi import HTTPException
from fastapi_sqlalchemy import db
from models.expense_model import Expense
from schemas.expense_schema import CreateExpenseSchema, UpdateExpenseSchema
from datetime import datetime

from sqlalchemy import and_

from fastapi_sqlalchemy import db
from models.expense_model import Expense
from models.cashBalance_model import CashBalance, TransactionType
from schemas.expense_schema import CreateExpenseSchema, UpdateExpenseSchema
from fastapi import HTTPException
from datetime import datetime

def create_expense(data: CreateExpenseSchema, user_id: int):
    try:
        with db.session.begin():
            expense = Expense(
                amount      = data.amount,
                category    = data.category,
                descriptions = data.descriptions,
                date        = data.date or datetime.now()
            )
            cash_log = CashBalance(
                transaction_type = TransactionType.EXPENSE,
                amount           = data.amount,
                reference_id     = None,
                notes            = f"{data.category}: {data.descriptions}",
                recorded_by      = user_id
            )

            db.session.add_all([expense, cash_log])

            db.session.flush()

            expense.cash_log_id = cash_log.id

        return expense
    except Exception as e:
        db.session.rollback()
        raise HTTPException(status_code=500, detail=str(e))


def get_all_expenses(
        start_date: str,
        end_date: str
):
    
    try:
        query = db.session.query(Expense)
        if start_date and end_date:
            query = query.filter(
                and_(Expense.date >= start_date, Expense.date < end_date)  
            )
            expenses = query.order_by(Expense.date.desc()).all()
            data = [expense.to_dict() for expense in expenses]
            return {
                "total": len(data),
                "data": data
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


    # expenses = (
    #     db.session
    #     .query(Expense)
    #     .order_by(Expense.date.desc())
    #     .all()
    # )
    # data = [expense.to_dict() for expense in expenses]
    # return {
    #     "total": len(data),
    #     "data": data
    # }


def get_expense_by_id(expense_id: int):
    expense = db.session.query(Expense).filter_by(id=expense_id).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    return expense.to_dict()

def update_expense(expense_id: int, data: UpdateExpenseSchema):
    expense = db.session.query(Expense).filter_by(id=expense_id).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")

    for key, value in data.dict(exclude_unset=True).items():
        setattr(expense, key, value)

    db.session.commit()
    return expense.to_dict()

def delete_expense(expense_id: int):
    expense = db.session.query(Expense).filter_by(id=expense_id).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")

    db.session.delete(expense)
    db.session.commit()
    return {"message": "Expense deleted successfully"}
