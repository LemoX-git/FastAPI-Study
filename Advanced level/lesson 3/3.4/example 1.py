from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import time

app = FastAPI()

# Синхронный генератор, который выдает числа
def generate_numbers():
    for i in range(5):
        time.sleep(1)  # Имитируем некоторую работу или задержку
        yield f"Число: {i}\n" # Каждое yield отправляет новый чанк

@app.get("/stream-numbers/")
async def stream_numbers():
    # Создаем StreamingResponse, передавая ему наш генератор
    return StreamingResponse(generate_numbers(), media_type="text/plain")