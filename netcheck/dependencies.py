from typing import Optional
from fastapi import Depends

# Example of a dependency (dependable)
# async def pyats_parameters(q: Optional[str] = None, success_rate: int = 0, failures: int = 0):
#     return {"q": q, "success_rate": success_rate, "failed": failures}

# Usage of a dependency
# @app.get("/test-results")
# async def test_results(results: dict = Depends(pyats_parameters)):
#     return results
