from fastapi import HTTPException
from fastapi_sqlalchemy import db
from models.expense_model import Expense
from schemas.expense_schema import CreateExpenseSchema, UpdateExpenseSchema
from datetime import datetime

from fastapi_sqlalchemy import db
from models.expense_model import Expense
from models.cashBalance_model import CashBalance, TransactionType
from schemas.expense_schema import CreateExpenseSchema, UpdateExpenseSchema
from fastapi import HTTPException
from datetime import datetime

def create_expense(data: CreateExpenseSchema, user_id: int):
    try:
        expense = Expense(
            amount=data.amount,
            category=data.category,
            description=data.description,
            date=data.date or datetime.now()
        )
        db.session.add(expense)

        cash_log = CashBalance(
            transaction_type=TransactionType.EXPENSE,
            amount=data.amount,
            reference_id=None,
            notes=f"{data.category}: {data.description}",
            recorded_by=user_id
        )
        db.session.add(cash_log)

        db.session.commit()
        return expense
    except Exception as e:
        db.session.rollback()
        raise HTTPException(status_code=500, detail=str(e))


def get_all_expenses():
    expenses = db.session.query(Expense).order_by(Expense.date.desc()).all()
    return [expense.to_dict() for expense in expenses]

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
