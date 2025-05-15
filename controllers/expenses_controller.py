from fastapi import APIRouter, HTTPException, Depends, Query
from schemas.expense_schema import CreateExpenseSchema, UpdateExpenseSchema
from services.expense_service import (
    create_expense, get_all_expenses, get_expense_by_id, update_expense, delete_expense
)
from services.jwt_utils import get_current_user
from datetime import datetime

router = APIRouter(prefix="/expenses", tags=["Expenses"])

@router.get("")
def get_expense_list(
    start_date: datetime = Query(
        ...,
        description="ISO datetime for the start of the period (required)"
    ),
    end_date: datetime = Query(
        ...,
        description="ISO datetime for the end of the period (required)"
    ),
    current_user: dict = Depends(get_current_user)
    ):
    return get_all_expenses(start_date=start_date, end_date=end_date)

@router.post("")
def create_expense_controller(
    data: CreateExpenseSchema,
    current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only admin can create expense")
    return create_expense(data, user_id=current_user["id"]) 


@router.get("/{expense_id}")
def get_expense(expense_id: int, current_user: dict = Depends(get_current_user)):
    return get_expense_by_id(expense_id)

@router.put("/{expense_id}")
def update_expense_controller(
    expense_id: int,
    data: UpdateExpenseSchema,
    current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only admin can update expense")
    return update_expense(expense_id, data, user_id=current_user["id"])

@router.delete("/{expense_id}")
def delete_expense_controller(expense_id: int, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only admin can delete expense")
    return delete_expense(expense_id)
