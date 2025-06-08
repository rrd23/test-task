# Сервис Уведомлений

Сервис на базе FastAPI для отправки email и Telegram уведомлений пользователям.

## Возможности

- Создание пользователей с email и опциональным Telegram ID
- Создание кампаний уведомлений
- Асинхронная отправка уведомлений через email и Telegram
- Отслеживание статуса каждого уведомления
- Поддержка Docker для простого развертывания
- Валидация email-адресов
- Безопасное хранение конфигурации
- Асинхронная обработка задач с Celery
- Интеграция с Telegram через aiogram

## Требования

- Docker и Docker Compose
- Python 3.11+ (для локальной разработки)
- PostgreSQL (управляется через Docker)
- Redis (управляется через Docker)

## Установка

1. Клонируйте репозиторий:
```bash
git clone <repository-url>
cd notification-service
```

2. Настройка переменных окружения:

   a. Создайте файл `.env` на основе `.env.example`:
   ```bash
   cp .env.example .env
   ```

   b. Отредактируйте `.env` файл, установив необходимые значения:
   - `APP_NAME` - название приложения
   - `APP_VERSION` - версия приложения
   - `DEBUG` - режим отладки (True/False)
   - `POSTGRES_*` - настройки базы данных
   - `REDIS_*` - настройки Redis
   - `TELEGRAM_BOT_TOKEN` - токен вашего Telegram бота
   - `SECRET_KEY` - секретный ключ для безопасности
   - `ALLOWED_HOSTS` - разрешенные хосты

   c. Для разработки рекомендуется установить:
   ```env
   DEBUG=True
   POSTGRES_HOST=localhost
   REDIS_HOST=localhost
   ```

   d. Для продакшена:
   ```env
   DEBUG=False
   POSTGRES_HOST=db
   REDIS_HOST=redis
   ```

3. Запустите сервисы с помощью Docker Compose:
```bash
docker-compose up --build
```

Сервис будет доступен по адресу `http://localhost:8000`

## API Документация

### Пользователи (Users)

#### Создание пользователя
```http
POST /users/
Content-Type: application/json

{
    "email": "user@example.com",
    "telegram_id": "123456789"  // опционально
}
```

**Ответ:**
```json
{
    "id": 1,
    "email": "user@example.com",
    "telegram_id": "123456789",
    "created_at": "2024-01-20T12:00:00"
}
```

#### Получение списка пользователей
```http
GET /users/
```

**Ответ:**
```json
[
    {
        "id": 1,
        "email": "user1@example.com",
        "telegram_id": "123456789",
        "created_at": "2024-01-20T12:00:00"
    },
    {
        "id": 2,
        "email": "user2@example.com",
        "telegram_id": "987654321",
        "created_at": "2024-01-20T12:30:00"
    }
]
```

#### Получение пользователя по ID
```http
GET /users/{user_id}
```

**Ответ:**
```json
{
    "id": 1,
    "email": "user@example.com",
    "telegram_id": "123456789",
    "created_at": "2024-01-20T12:00:00"
}
```

#### Обновление пользователя
```http
PATCH /users/{user_id}
Content-Type: application/json

{
    "telegram_id": "123456789"  // опционально
}
```

**Ответ:**
```json
{
    "id": 1,
    "email": "user@example.com",
    "telegram_id": "123456789",
    "created_at": "2024-01-20T12:00:00"
}
```

**Описание:**
- Обновляет данные пользователя
- Поддерживает частичное обновление (можно обновить только telegram_id)
- Возвращает обновленные данные пользователя

### Кампании (Campaigns)

#### Создание новой рассылки
```http
POST /campaigns/
Content-Type: application/json

{
    "text": "Ваше сообщение уведомления",
    "user_ids": [1, 2, 3]
}
```

**Ответ:**
```json
{
    "id": 1,
    "text": "Ваше сообщение уведомления",
    "created_at": "2024-01-20T13:00:00",
    "users": [
        {
            "user": {
                "id": 1,
                "email": "user1@example.com",
                "telegram_id": "123456789"
            },
            "status": "pending"
        },
        {
            "user": {
                "id": 2,
                "email": "user2@example.com",
                "telegram_id": "987654321"
            },
            "status": "pending"
        }
    ]
}
```

**Описание:**
- Создает новую рассылку уведомлений
- Отправляет уведомления всем указанным пользователям
- Поддерживает отправку через email и Telegram (если указан telegram_id)
- Асинхронно обрабатывает отправку уведомлений
- Возвращает созданную кампанию со статусами отправки для каждого пользователя

#### Получение статуса кампании
```http
GET /campaigns/{campaign_id}/status
```

**Ответ:**
```json
{
    "id": 1,
    "status": "completed",
    "total_notifications": 3,
    "sent_notifications": 3,
    "failed_notifications": 0,
    "created_at": "2024-01-20T13:00:00",
    "completed_at": "2024-01-20T13:01:00"
}
```

#### Получение списка кампаний
```http
GET /campaigns/
```

**Ответ:**
```json
[
    {
        "id": 1,
        "text": "Первая кампания",
        "status": "completed",
        "created_at": "2024-01-20T13:00:00"
    },
    {
        "id": 2,
        "text": "Вторая кампания",
        "status": "pending",
        "created_at": "2024-01-20T14:00:00"
    }
]
```

### Примеры использования с curl

#### Создание пользователя
```bash
curl -X POST "http://localhost:8000/users/" \
     -H "Content-Type: application/json" \
     -d '{
           "email": "user@example.com",
           "telegram_id": "123456789"
         }'
```

#### Обновление пользователя
```bash
curl -X PATCH "http://localhost:8000/users/1" \
     -H "Content-Type: application/json" \
     -d '{
           "telegram_id": "123456789"
         }'
```

#### Создание кампании
```bash
curl -X POST "http://localhost:8000/campaigns/" \
     -H "Content-Type: application/json" \
     -d '{
           "text": "Привет, мир!",
           "user_ids": [1, 2, 3]
         }'
```

#### Проверка статуса кампании
```bash
curl "http://localhost:8000/campaigns/1/status"
```

### Примеры использования с Python

```python
import requests

BASE_URL = "http://localhost:8000"

# Создание пользователя
def create_user(email: str, telegram_id: str = None):
    response = requests.post(
        f"{BASE_URL}/users/",
        json={
            "email": email,
            "telegram_id": telegram_id
        }
    )
    return response.json()

# Обновление пользователя
def update_user(user_id: int, telegram_id: str = None):
    response = requests.patch(
        f"{BASE_URL}/users/{user_id}",
        json={
            "telegram_id": telegram_id
        }
    )
    return response.json()

# Создание кампании
def create_campaign(text: str, user_ids: list):
    response = requests.post(
        f"{BASE_URL}/campaigns/",
        json={
            "text": text,
            "user_ids": user_ids
        }
    )
    return response.json()

# Проверка статуса кампании
def get_campaign_status(campaign_id: int):
    response = requests.get(f"{BASE_URL}/campaigns/{campaign_id}/status")
    return response.json()

# Пример использования
if __name__ == "__main__":
    # Создаем пользователя
    user = create_user("user@example.com", "123456789")
    print(f"Создан пользователь: {user}")

    # Обновляем telegram_id пользователя
    updated_user = update_user(user["id"], "987654321")
    print(f"Обновлен пользователь: {updated_user}")

    # Создаем кампанию
    campaign = create_campaign("Тестовое сообщение", [user["id"]])
    print(f"Создана кампания: {campaign}")

    # Проверяем статус
    status = get_campaign_status(campaign["id"])
    print(f"Статус кампании: {status}")
```

### Коды ответов

- `200 OK` - Успешный запрос
- `201 Created` - Успешное создание ресурса
- `400 Bad Request` - Неверный формат запроса
- `404 Not Found` - Ресурс не найден
- `422 Unprocessable Entity` - Ошибка валидации данных
- `500 Internal Server Error` - Внутренняя ошибка сервера

### Ограничения

- Максимальный размер текста уведомления: 1000 символов
- Максимальное количество пользователей в одной кампании: 1000
- Минимальный интервал между кампаниями: 1 минута

## Разработка

Для локальной разработки:

1. Создайте виртуальное окружение:
```bash
python -m venv venv
source venv/bin/activate  # На Windows: venv\Scripts\activate
```

2. Установите зависимости:
```bash
pip install -r requirements.txt
```

3. Создайте и настройте файл `.env` (см. выше)

4. Запустите приложение:
```bash
uvicorn app.main:app --reload
```

## Зависимости

Основные зависимости проекта:
- FastAPI - веб-фреймворк
- SQLAlchemy - ORM для работы с базой данных
- Celery - асинхронная обработка задач
- Redis - брокер сообщений для Celery
- aiogram - библиотека для работы с Telegram API
- python-dotenv - загрузка переменных окружения
- email-validator - валидация email-адресов
- python-jose - работа с JWT токенами
- passlib - хеширование паролей
- aiohttp - асинхронные HTTP-запросы
- tenacity - повторные попытки выполнения операций

## Примеры использования

1. Создание пользователя:
```bash
curl -X POST "http://localhost:8000/users/" \
     -H "Content-Type: application/json" \
     -d '{"email": "user@example.com", "telegram_id": "123456789"}'
```

2. Обновление пользователя:
```bash
curl -X PATCH "http://localhost:8000/users/1" \
     -H "Content-Type: application/json" \
     -d '{"telegram_id": "987654321"}'
```

3. Создание кампании:
```bash
curl -X POST "http://localhost:8000/campaigns/" \
     -H "Content-Type: application/json" \
     -d '{"text": "Привет, мир!", "user_ids": [1]}'
```

4. Проверка статуса кампании:
```bash
curl "http://localhost:8000/campaigns/1/status"
``` 