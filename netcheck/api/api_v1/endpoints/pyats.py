from fastapi import APIRouter, HTTPException
from sqlmodel import Session, select
from typing import List
from backend.models import TestResults, TestResultsRead
from backend.db import engine

router = APIRouter()

@router.get("/tests", response_model=List[TestResultsRead], tags=["pyats"])
def get_test_results():
    with Session(engine) as session:
        results = session.exec(select(TestResults)).all()
        return results

@router.get("/tests/{test_id}", response_model=TestResultsRead, tags=["pyats"])
def get_single_test_result(test_id: int):
    with Session(engine) as session:
        test_result = session.get(TestResults, test_id)
        if not test_result:
            raise HTTPException(status_code=404, detail="No test results found")
        return test_result
