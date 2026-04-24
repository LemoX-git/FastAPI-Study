# Импортируем необходимые библиотеки
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Создаём приложение FastAPI
app = FastAPI(title="Messages CRUD")

# Настраиваем CORS для взаимодействия с фронтендом
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Модель Pydantic для создания нового сообщения
class MessageCreate(BaseModel):
    content: str

# Модель Pydantic для частичного обновления сообщения
class MessageUpdate(BaseModel):
    content: str | None = None

# Модель Pydantic для представления сообщения в ответах API
class Message(BaseModel):
    id: int
    content: str

# Простая "база данных" в памяти для хранения сообщений
messages_db: list[Message] = [Message(id=0, content="First post in FastAPI")]

# Функция для генерации следующего ID
def next_id() -> int:
    return max((m.id for m in messages_db), default=-1) + 1

def get_index(message_id: int) -> int:
    for i, m in enumerate(messages_db):
        if m.id == message_id:
            return i
    return -1

# Эндпоинт для получения списка сообщений
@app.get("/messages", response_model=list[Message])
async def list_messages() -> list[Message]:
    return messages_db

# Эндпоинт для создания сообщения
@app.post("/messages", response_model=Message, status_code=201)
async def create_message(payload: MessageCreate) -> Message:
    m = Message(id=next_id(), content=payload.content)
    messages_db.append(m)
    return m

# Эндпоинт для получения одного сообщения
@app.get("/messages/{message_id}", response_model=Message)
async def get_message(message_id: int) -> Message:
    idx = get_index(message_id)
    if idx < 0:
        raise HTTPException(status_code=404, detail="Message not found")
    return messages_db[idx]

# Эндпоинт для частичного обновления сообщения
@app.patch("/messages/{message_id}", response_model=Message)
async def update_message(message_id: int, payload: MessageUpdate) -> Message:
    # Ищем индекс сообщения по ID
    idx = get_index(message_id)
    
    # Если сообщение не найдено, возвращаем ошибку 404
    if idx < 0:
        raise HTTPException(status_code=404, detail="Message not found")
    
    # Обновляем только переданные поля
    if payload.content is not None:
        messages_db[idx].content = payload.content
    
    return messages_db[idx]

# Эндпоинт для полной замены сообщения
@app.put("/messages/{message_id}", response_model=Message)
async def replace_message(message_id: int, payload: MessageCreate) -> Message:
    idx = get_index(message_id)
    if idx < 0:
        raise HTTPException(status_code=404, detail="Message not found")
    updated = Message(id=message_id, content=payload.content)
    messages_db[idx] = updated
    return updated

# Эндпоинт для удаления сообщения
@app.delete("/messages/{message_id}", status_code=204)
async def delete_message(message_id: int):
    # Ищем индекс сообщения по ID
    idx = get_index(message_id)
    
    # Если сообщение не найдено, возвращаем ошибку 404
    if idx < 0:
        raise HTTPException(status_code=404, detail="Message not found")
    
    # Удаляем сообщение из базы данных
    messages_db.pop(idx)