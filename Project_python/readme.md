# FastAPI Auth Project

🚀 Простой и чистый backend на FastAPI с JWT-авторизацией и асинхронной работой с базой данных.

## 📦 Используемый стек

- **FastAPI** — современный web-фреймворк
- **SQLAlchemy 2.0 (async)** — работа с БД
- **PostgreSQL** — СУБД
- **JWT (PyJWT)** — авторизация (access и refresh токены)
- **Pydantic v2** — валидация данных
- **Uvicorn** — ASGI-сервер

## 🧠 Реализовано

- Регистрация пользователей
- Логин
- Выдача `access` и `refresh` токенов
- Проверка и обновление access токена
- Хранение refresh токенов в базе
- Защищённые эндпоинты с токенами
- Асинхронная работа с БД
- Разделение логики по слоям (service, jwt, db и т.д.)

## 🛠 Как запустить

1. Клонировать проект:
   ```bash
   git clone https://github.com/your_username/your_repo.git
   cd your_repo