from typing import Optional
from sqlalchemy.sql.expression import table
from sqlmodel import Field, SQLModel
from datetime import datetime

# class Device(SQLModel):
#     hostname: str
#     ip: str
#     os: Optional[str] = None
class TestResultsBase(SQLModel):
    name: str
    executed_at: datetime
    success_rate: float
    failure_rate: float
    tests_passed: int
    tests_failed: int

class TestResults(TestResultsBase, table=True):
    test_id: Optional[int] = Field(default=None, primary_key=True)

class TestResultsRead(TestResultsBase):
    test_id: int

class TestResultsDelete(TestResultsBase):
    test_id: int