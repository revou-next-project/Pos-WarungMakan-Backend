from fastapi import APIRouter, HTTPException, Depends, Query
from schemas.income_schema import CreateIncomeSchema

from services.income_service import (
    create_income, get_all_incomes
)

from datetime import datetime
from services.jwt_utils import get_current_user
from datetime import datetime

router = APIRouter(prefix="/incomes", tags=["Incomes"])

@router.get("")
async def get_incomes_list(
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
    return await get_all_incomes(start_date=start_date, end_date=end_date)

@router.post("")
async def create_income_controller(
    income_data: CreateIncomeSchema,
    current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only admin can create an income")
    return await create_income(income_data, user_id=current_user["id"])
