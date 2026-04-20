from fastapi import FastAPI, status, Body
from fastapi.exceptions import HTTPException
from pydantic import BaseModel

app = FastAPI(debug = True)

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
async def create_message(message: Message) -> Message:
    if any(msg.id == message.id for msg in messages_db):
        raise(HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="The message ID already exists"))
    messages_db.append(message)
    return message


@app.put("/messages/{message_id}", response_model=Message, status_code=status.HTTP_200_OK)
async def update_message(message_id: int, message: Message) -> str:
    if message_id != message.id:
        raise(HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="The ID in the request body must match the ID in the path"))

    if not any(msg.id == message.id for msg in messages_db):
        raise(HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found"))
    
    for msg in messages_db:
        if msg.id == message_id:
            msg.content = message.content
            return msg


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