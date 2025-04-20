from fastapi import APIRouter, HTTPException, Depends
from schemas.employee_schema import EmployeeCreateSchema, EmployeeUpdateSchema

from services import employee_service
from services.jwt_utils import get_current_user

router = APIRouter(prefix="/employees", tags=["Employees"])

@router.get("")
def list_employees():
    return [emp.to_dict() for emp in employee_service.get_all_employees()]

@router.get("/{employee_id}")
def get_employee(employee_id: int):
    return employee_service.get_employee_by_id(employee_id).to_dict()

@router.post("")
def create_employee(data: EmployeeCreateSchema, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only admin can create employee")
    return employee_service.create_employee(data).to_dict()

@router.put("/{employee_id}")
def update_employee(employee_id: int, data: EmployeeUpdateSchema, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only admin can update employee")
    return employee_service.update_employee(employee_id, data).to_dict()

@router.delete("/{employee_id}")
def delete_employee(employee_id: int, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only admin can delete employee")
    return employee_service.delete_employee(employee_id)
