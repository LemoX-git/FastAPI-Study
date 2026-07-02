from fastapi import FastAPI, APIRouter, HTTPException, status


app = FastAPI()


company_router = APIRouter(prefix="/company", tags=["Company"])

@company_router.get("/")
async def get_root_company() -> str:
    return f"This is the company level"


departament_router = APIRouter(prefix="/departments/{dept_id}", tags=["Departaments"])

@departament_router.get("/")
async def get_root_departament(dept_id: int) -> str:
    return f"This is department {dept_id}"


teams_router = APIRouter(prefix="/teams/{team_id}", tags=["Teams"],)

@teams_router.get("/")
async def get_root_teams(team_id: int, dept_id: int) -> str:
    return f"This is team {team_id} in department {dept_id}"


employees_router = APIRouter(prefix="/employees/{emp_id}", tags=["Employees"],)

@employees_router.get("/")
async def get_root_employees(emp_id: int, team_id: int, dept_id: int) -> str:
    return f"This is employee {emp_id} in team {team_id}, department {dept_id}"


teams_router.include_router(employees_router)
departament_router.include_router(teams_router)
company_router.include_router(departament_router)

app.include_router(company_router, prefix="/api")