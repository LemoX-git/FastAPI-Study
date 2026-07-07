from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from typing import Optional
import re  # Для парсинга Accept заголовка

# Импортируем модели для разных версий продуктов
from api_versions.products.v1_models import ProductV1
from api_versions.products.v2_models import ProductV2

app = FastAPI(
    title="Content Negotiation Versioning Example",
    description="Пример реализации версионирования API",
    version="1.0.0"
)


# --- Вспомогательная функция для определения версии из Accept заголовка ---
def get_api_version_from_accept(accept_header: Optional[str]) -> Optional[str]:
    """
    Парсит заголовок Accept для определения запрошенной версии API.
    Ожидаемый формат: application/vnd.mycompany.v<VERSION>+json
    """
    if not accept_header:
        return None  # Или можно вернуть версию по умолчанию

    # Регулярное выражение для извлечения версии
    # Ищем что-то вроде "v1" или "v2" после "vnd.mycompany." и до "+json"
    match = re.search(r'application/vnd\.mycompany\.v(\d+)\+json', accept_header)
    if match:
        return match.group(1)  # Возвращаем найденную цифру версии
    return None


# --- Эндпоинт для получения списка продуктов ---
@app.get(
    "/products/",
    summary="Get a list of products (Content Negotiated)"
)
async def get_products(request: Request) -> Response:
    """
    Получает список продуктов, версионированных по заголовку `Accept`.

    - Запрос с `Accept: application/vnd.mycompany.v1+json` вернет данные V1.
    - Запрос с `Accept: application/vnd.mycompany.v2+json` вернет данные V2.
    - Если заголовок `Accept` отсутствует или не содержит информации о версии,
      будет возвращена ошибка 406 Not Acceptable.
    """
    accept_header = request.headers.get("accept")
    requested_version = get_api_version_from_accept(accept_header)

    if not requested_version:
        raise HTTPException(
            status_code=406,
            detail="Not Acceptable. Please specify a supported API version in the Accept header (e.g., Accept: application/vnd.mycompany.v1+json)."
        )

    if requested_version == "1":
        # Логика и данные для V1
        products_data_v1 = [
            ProductV1(id=1, name="Laptop Basic", price=1200.0),
            ProductV1(id=2, name="Mouse Wireless", price=25.0)
        ]
        # Важно: устанавливаем Content-Type, соответствующий запрошенной версии
        return JSONResponse(
            content=[p.model_dump() for p in products_data_v1],
            # Используем model_dump() для сериализации
            media_type="application/vnd.mycompany.v1+json"
        )

    elif requested_version == "2":
        # Логика и данные для V2
        products_data_v2 = [
            ProductV2(product_id="LPT001", product_name="Super Laptop Pro", current_price=1800.0,
                      currency="USD", description="High-performance laptop for professionals."),
            ProductV2(product_id="MOU005", product_name="Ergo Mouse Elite", current_price=45.0,
                      currency="EUR", description="Ergonomic mouse with customizable buttons.")
        ]
        # Важно: устанавливаем Content-Type, соответствующий запрошенной версии
        return JSONResponse(
            content=[p.model_dump() for p in products_data_v2],
            # Используем model_dump() для сериализации
            media_type="application/vnd.mycompany.v2+json"
        )

    else:
        # Если версия найдена, но не поддерживается нашим кодом (хотя get_api_version_from_accept уже отсеет большинство)
        raise HTTPException(
            status_code=400,  # Bad Request, так как клиент запросил неподдерживаемую версию
            detail=f"API Version {requested_version} is not supported for this resource."
        )


@app.get("/")
async def root():
    return {
        "message": "Welcome to Content Negotiation Versioning Example! Check /docs for details."}
