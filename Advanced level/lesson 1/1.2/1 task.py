from typing import Annotated

from fastapi import (
    FastAPI,
    APIRouter,
    HTTPException,
    status,
    Path,
)
from fastapi.responses import PlainTextResponse


app = FastAPI()


router_v1 = APIRouter(prefix="/api/v1", tags=["v1 Tasks"])
router_v2 = APIRouter(prefix="/api/v2", tags=["v2 Tasks"])


@router_v1.get("/tasks", response_class=PlainTextResponse)
async def get_tasks_v1() -> str:
    return "Tasks in v1: Task 1, Task 2"

@router_v1.get("/tasks/{task_id}", response_class=PlainTextResponse)
async def get_task_by_id_v1(
    task_id: Annotated[int, Path(gt=0)],
) -> str:
    return f"Task {task_id} in v1"


@router_v2.get("/tasks", response_class=PlainTextResponse)
async def get_tasks_v2() -> str:
    return "Tasks in v2: Task 1 (open), Task 2 (closed)"

@router_v2.get("/tasks/{task_id}", response_class=PlainTextResponse)
async def get_task_by_id_v2(
    task_id: int,
) -> str:
    if task_id < 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid task ID")
    
    return f"Task {task_id} in v2 with status: open"

@router_v2.get("/tasks/count", response_class=PlainTextResponse)
async def get_tasks_count_v2() -> str:
    return "Total tasks in v2: 2"


app.include_router(router_v1)
app.include_router(router_v2)