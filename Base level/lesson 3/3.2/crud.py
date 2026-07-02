from fastapi import FastAPI, status, Body
from fastapi.exceptions import HTTPException
from pydantic import BaseModel

app = FastAPI(debug = True)

class MessageCreate(BaseModel):
    content: str

class Message(BaseModel):
    id: int
    content: str

messages_db: list[Message] = [Message(id=0, content="First post")] 


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
    next_id = len(messages_db) if messages_db else 0
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