from fastapi import APIRouter, Depends, HTTPException
from services.cashbalance_service import get_cashflow_summary
from services.jwt_utils import get_current_user

router = APIRouter(prefix="/cashflow", tags=["CashFlow"])

@router.get("/summary")
async def get_cashflow_summary_controller(
    period: str = "day",  # default to daily summary
    page: int = 1,        # default page number
    limit: int = 10,      # default records per page
    start_date: str = None,  # optional start date
    end_date: str = None,    # optional end date
    transaction_type: str = None,  # filter by 'SALE' or 'EXPENSE'
    current_user: dict = Depends(get_current_user)  # check if user is logged in and authorized
):
    if current_user["role"] not in ["admin", "cashier"]:
        raise HTTPException(status_code=403, detail="Admin or Cashier only")

    try:
        cashflow_data = get_cashflow_summary(
            period=period, 
            page=page, 
            limit=limit,
            start_date=start_date,
            end_date=end_date,
            transaction_type=transaction_type  # Pass the filter to the service
        )
        return cashflow_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
