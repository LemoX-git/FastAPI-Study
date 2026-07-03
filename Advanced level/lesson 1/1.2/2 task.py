from typing import Annotated

from fastapi import (
    FastAPI,
    APIRouter,
    HTTPException,
    status,
    Header,
    Depends,
)
from fastapi.responses import PlainTextResponse


app = FastAPI()


router = APIRouter(prefix="/api/notes")


async def get_api_version(
    api_version: Annotated[str | None, Header(alias="X-API-Version")] = None,
) -> str:
    if api_version not in ("v1", "v2"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or missing API version",
        )

    return api_version


@router.get('/', response_class=PlainTextResponse)
async def get_notes(
    api_version: Annotated[str, Depends(get_api_version)],
) -> str:
    if api_version == "v1":
        return "Notes in v1: Note 1, Note 2"
    elif api_version == "v2":
        return "Notes in v2: Note 1 (draft), Note 2 (published)"
    

@router.get("/count", response_class=PlainTextResponse)
async def get_notes_count(
    api_version: Annotated[str, Depends(get_api_version)],
) -> str:
    if api_version == "v2":
        return "Total notes in v2: 2"
    elif api_version == "v1":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or missing API version",
        )


@router.get("/{note_id}", response_class=PlainTextResponse)
async def get_note_by_id(
    note_id: int,
    api_version: Annotated[str, Depends(get_api_version)],
) -> str:
    if note_id < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid note ID",
        )

    if api_version == "v1":
        return f"Note {note_id} in v1"
    elif api_version == "v2":
        return f"Note {note_id} in v2 with status: draft"
    

app.include_router(router)