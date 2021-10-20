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
    total_tests: int
    tests_passed: int
    tests_failed: int

    def __iter__(self):
        yield "name", self.name
        yield "executed_at", self.executed_at
        yield "success_rate", self.success_rate
        yield "total_tests", self.total_tests
        yield "tests_passed", self.tests_passed
        yield "tests_failed", self.tests_failed


class TestResults(TestResultsBase, table=True):
    test_id: Optional[int] = Field(default=None, primary_key=True)


class TestResultsRead(TestResultsBase):
    test_id: int


class TestResultsDelete(TestResultsBase):
    test_id: int
