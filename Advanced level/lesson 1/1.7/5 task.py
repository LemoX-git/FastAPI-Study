from fastapi import FastAPI, Response
from fastapi.responses import RedirectResponse, JSONResponse


app = FastAPI()


@app.get("/check/{value}", response_class=Response)
async def root(value: int) -> Response:
    if value > 10:
        return RedirectResponse(url="/high", status_code=302)
    else:
        return JSONResponse(content={"status": "Low value"}, status_code=200)
    

@app.get("/high", response_class=JSONResponse, status_code=200)
async def root2() -> JSONResponse:
    return JSONResponse(content={"status": "High value"})