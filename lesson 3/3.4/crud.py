from fastapi import FastAPI, HTTPException, status, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel


app = FastAPI(debug = True)

# Настройка Jinja2 и статических файлов
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Модель для входных данных (запросов: создание и обновление)
class MessageCreate(BaseModel):
    content: str

# Модель для ответов и хранения в базе данных
class Message(BaseModel):
    id: int
    content: str

# Инициализируем messages_db как список объектов Message
messages_db: list[Message] = [Message(id=0, content="Первое сообщение в FastAPI")]


@app.get("/messages", response_model=list[Message])
async def read_messages() -> list[Message]:
    return messages_db


@app.get("/messages/{message_id}", response_model=Message)
async def read_message(message_id: int) -> Message:
    for message in messages_db:
        if message.id == message_id:
            return message
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


@app.post("/messages", response_model=Message, status_code=status.HTTP_201_CREATED)
async def create_message(input_message: MessageCreate) -> Message:
    next_id = len(messages_db) if messages_db else 0    # Полная шляпа, так как при изменениях контейнера будут нарушения нумерации id
    new_massege = Message(id=next_id, content=input_message.content)
    messages_db.append(new_massege)
    return new_massege


@app.put("/messages/{message_id}", response_model=Message, status_code=status.HTTP_200_OK)
async def update_message(message_id: int, input_message: MessageCreate) -> str:
    if not any(msg.id == message_id for msg in messages_db):
        raise(HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found"))
    
    messages_db[message_id].content = input_message.content
    return messages_db[message_id]


@app.delete("/messages", status_code=status.HTTP_200_OK)
async def delete_messages() -> dict:
    messages_db.clear()
    return {"detail": "All messages deleted!"}


@app.delete("/messages/{message_id}", status_code=status.HTTP_200_OK)
async def delete_message(message_id: int) -> dict:
    if not any(msg.id == message_id for msg in messages_db):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")
    
    messages_db.pop(message_id)
    return {"detail": f"Message ID={message_id} deleted!"}


@app.get("/web/messages", response_class=HTMLResponse)
async def get_messages_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"messages": messages_db},
    )


# Страница создания сообщения
@app.get("/web/messages/create", response_class=HTMLResponse)
async def get_create_message_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="create.html"
    )


# Обработка формы создания сообщения
@app.post("/web/messages", response_class=HTMLResponse)
async def create_message_form(request: Request, content: str = Form(...)):
    next_id = max((msg.id for msg in messages_db), default=-1) + 1
    new_message = Message(id=next_id, content=content)
    messages_db.append(new_message)
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"messages": messages_db},
    )


# Страница одного сообщения
@app.get("/web/messages/{message_id}", response_class=HTMLResponse)
async def get_message_detail_page(request: Request, message_id: int):
    for message in messages_db:
        if message.id == message_id:
            return templates.TemplateResponse(
                request=request,
                name="detail.html",
                context={"message": message},
            )
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Сообщение не найдено")