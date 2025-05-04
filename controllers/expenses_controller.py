from fastapi import APIRouter, HTTPException, Depends
from schemas.expense_schema import CreateExpenseSchema, UpdateExpenseSchema
from services.expense_service import (
    create_expense, get_all_expenses, get_expense_by_id, update_expense, delete_expense
)
from services.jwt_utils import get_current_user

router = APIRouter(prefix="/expenses", tags=["Expenses"])

@router.get("")
def get_expense_list(current_user: dict = Depends(get_current_user)):
    return get_all_expenses()

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
