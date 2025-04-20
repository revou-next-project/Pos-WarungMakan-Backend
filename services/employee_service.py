from fastapi import HTTPException
from fastapi_sqlalchemy import db
from models.employee_model import Employee
from schemas.employee_schema import EmployeeCreateSchema, EmployeeUpdateSchema

def get_all_employees():
    return db.session.query(Employee).all()

def get_employee_by_id(employee_id: int):
    employee = db.session.query(Employee).filter_by(id=employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee

def create_employee(data: EmployeeCreateSchema):
    employee = Employee(**data.dict())
    db.session.add(employee)
    db.session.commit()
    return employee

def update_employee(employee_id: int, data: EmployeeUpdateSchema):
    employee = db.session.query(Employee).filter_by(id=employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    for key, value in data.dict(exclude_unset=True).items():
        setattr(employee, key, value)
    db.session.commit()
    return employee

def delete_employee(employee_id: int):
    employee = db.session.query(Employee).filter_by(id=employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    db.session.delete(employee)
    db.session.commit()
    return {"message": "Employee deleted"}
