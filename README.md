# Workshop Booking System

Серверная часть системы управления бронированием мастер-классов на **Django** и **Django REST Framework**. Данные хранятся в **PostgreSQL**. Клиент для проверки API — коллекция **Postman**.

## Возможности

- регистрация и вход с выдачей токена;
- публичный просмотр списка и деталей мастер-классов;
- CRUD мастер-классов только для роли `admin`;
- запись на мастер-класс только для авторизованных пользователей;
- просмотр и отмена **своих** бронирований;
- запрет повторной записи, записи на прошедшую дату и превышения вместимости.

## Архитектура

| Модуль | Назначение |
| --- | --- |
| `users` | Модель пользователя с ролями, регистрация, вход, права `IsAdminRole` |
| `workshops` | Модель мастер-класса, сериализаторы, сервис CRUD, ViewSet |
| `bookings` | Модель брони, уникальность пары пользователь–мастер-класс, сервис валидации |
| `config` | Настройки проекта и маршруты REST API |

Связи:

- `User` - `Workshop` (создатель);
- `User` - `Booking`;
- `Workshop` - `Booking`;
- ограничение `unique_user_workshop_booking` запрещает дубли брони.

Оптимизация запросов: `select_related` / `annotate(Count)` в сервисах, чтобы не было N+1.

## Запуск через Docker

Нужны Docker и Docker Compose.

```bash
copy .env.example .env
docker compose up --build
```

API: `http://localhost:8000/api/`  
Админка Django: `http://localhost:8000/admin/`

После старта команда `seed_demo` создаёт тестовые учётные записи:

| Логин | Пароль | Роль |
| --- | --- | --- |
| `admin` | `AdminPass123` | администратор |
| `user` | `UserPass123` | пользователь |

## REST API

Аутентификация: заголовок `Authorization: Token <ключ>`.

| Метод | URL | Кто | Описание |
| --- | --- | --- | --- |
| POST | `/api/auth/register/` | все | регистрация, ответ с токеном |
| POST | `/api/auth/login/` | все | вход, ответ с токеном |
| GET | `/api/auth/me/` | авторизованный | текущий пользователь |
| GET | `/api/workshops/` | все | список мастер-классов |
| GET | `/api/workshops/{id}/` | все | детали мастер-класса |
| POST | `/api/workshops/` | admin | создать |
| PUT / PATCH | `/api/workshops/{id}/` | admin | обновить |
| DELETE | `/api/workshops/{id}/` | admin | удалить |
| GET | `/api/bookings/` | авторизованный | свои брони |
| GET | `/api/bookings/{id}/` | авторизованный | своя бронь |
| POST | `/api/bookings/` | авторизованный | тело `{"workshop_id": 1}` |
| DELETE | `/api/bookings/{id}/` | авторизованный | отмена брони |

Ответы — JSON. Пароли и хеши в API не возвращаются. В брони вложен объект `workshop`.

## Postman

1. Импортируйте `postman/Workshop_Booking.postman_collection.json`.
2. Импортируйте окружение `postman/Workshop_Booking.postman_environment.json` (переменная `base_url`).
3. Запустите **Collection Runner** целиком: в запросах есть автотесты кодов ответа, сохранение токенов и id в переменные коллекции.

Порядок в коллекции: регистрация/вход → публичный список мастер-классов → CRUD от админа → брони (включая 401, дубль и прошедшую дату) → отмена брони.

## Локальный запуск без Docker

Нужен PostgreSQL с параметрами из `.env`.

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
# в .env укажите POSTGRES_HOST=localhost
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

## Тесты Django

```bash
python manage.py test --settings=config.test_settings
```
