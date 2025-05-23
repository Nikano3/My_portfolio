# 🚀 FastAPI Auth API (pet-проект)

Небольшой проект на FastAPI с авторизацией через JWT. Сделал для практики — есть регистрация, логин, защищённые эндпоинты, работа с PostgreSQL, хэширование паролей и тесты.

---

## 🔧 Что умеет

* Регистрация и вход
* JWT access/refresh токены
* Защищённые маршруты (доступ только с access токеном)
* Обновление access токена через refresh
* Хэширование паролей
* Асинхронная работа с PostgreSQL
* Простая HTML-форма регистрации на `/`
* Тесты через pytest

---

## 🧰 Стек

* FastAPI
* SQLAlchemy (async)
* PostgreSQL
* Pydantic
* JWT
* Uvicorn
* Pytest
* hashlib

---

## 📁 Структура

```
Project_python/
│
├── app/
│   ├── database/
│   │   └── users/
│   │       ├── db.py          # подключение к БД
│   │       ├── models.py      # модели
│   │       └── user.py        # логика по юзерам
│   ├── schemas/
│   │   └── schema.py          # Pydantic-схемы
│   ├── utils/
│   │   ├── jwt_operations.py  # токены
│   │   └── password.py        # хэши
│   ├── config.py
│   └── main.py
│
├── frontend/                  # HTML/JS
├── tests/                     # pytest
├── .env
├── pytest.ini
├── requirements.txt
└── venv/
```

---

## ⚙️ Как запустить

1. Клонируй проект:

```bash
git clone https://github.com/yourname/your-repo.git
cd your-repo
```

2. Создай виртуалку и активируй:

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. Установи зависимости:

```bash
pip install -r requirements.txt
```

4. Создай `.env` в корне:

```env
POSTGRES_SERVER=localhost
POSTGRES_USER=youruser
POSTGRES_PASSWORD=yourpass
POSTGRES_DB=yourdb
JWT_SECRET=your_jwt_secret
JWT_LIFETIME=30
```

5. Запусти сервер:

```bash
uvicorn app.main:app --reload
```

6. Открой в браузере:

* Документация: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* HTML-форма: [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

## 📌 Эндпоинты

| Метод | URL                   | Защита | Описание                              |
| ----- | --------------------- | ------ | ------------------------------------- |
| GET   | `/`                   | ❌      | HTML-форма регистрации                |
| POST  | `/users/registration` | ❌      | Регистрация                           |
| POST  | `/users/login`        | ❌      | Вход                                  |
| POST  | `/refresh`            | ❌      | Обновление access токена              |
| GET   | `/users`              | ✅      | Все пользователи (нужен access токен) |
| GET   | `/users/{id}`         | ✅      | Один пользователь (access токен)      |

> ❌ — не требует токен
> ✅ — нужен валидный access токен

---

## 🧪 Тесты

```bash
pytest
```

---

## 📄 Лицензия

Pet-проект без лицензии. Используйте как хотите, особенно для обучения.

---

## 👤 Автор

Делал для практики. Контакты позже добавлю в GitHub, когда залью.
