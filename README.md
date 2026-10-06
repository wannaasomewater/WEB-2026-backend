# WEB-2026-backend — Electrical Appliances EMF API

REST API для системы оценки электромагнитного излучения от электронных приборов.

## Стек
- FastAPI
- SQLAlchemy (ORM)
- Alembic (миграции)
- PostgreSQL
- SeaweedFS (S3-совместимое хранилище, замена MinIO)
- boto3 (S3-клиент)

## Запуск
1. docker-compose up -d
2. source emf_devices_venv/bin/activate
3. alembic upgrade head
4. python main.py

Swagger: http://127.0.0.1:8000/docs

## HTTP-методы

### Домен: Услуги (electrical_appliances)

| Метод | URL | Описание |
|-------|-----|----------|
| GET | /api/appliances | Список опубликованных с фильтром max_power |
| GET | /api/appliances/feed | Лента с признаком is_liked |
| GET | /api/appliances/draft | Черновик пользователя |
| POST | /api/appliances | Создание с файлами (multipart) |
| PUT | /api/appliances/{id}/publish | Публикация |
| DELETE | /api/appliances/{id} | Мягкое удаление (SQL UPDATE) |
| POST | /api/appliances/{id}/like | Лайк (value=0/1) |

### Домен: Пользователи (users)

| Метод | URL | Описание |
|-------|-----|----------|
| POST | /api/users/register | Регистрация |
| POST | /api/users/login | Аутентификация (заглушка) |
| POST | /api/users/logout | Деавторизация (заглушка) |

## Таблицы БД

### electrical_appliances
id (PK), appliance_name, power_consumption, frequency, emf_level, safety_distance, description, status, image_url, video_url, created_at, created_by, published_at

### users
id (PK), username, full_name, password_hash, role

### device_likes
id (PK), user_id (FK users.id), appliance_id (FK electrical_appliances.id)

## Архитектура
- api/ — роутеры FastAPI
- core/ — конфигурация (config, current_user)
- db/ — БД (base, session)
- models/ — модели SQLAlchemy
- schemas/ — Pydantic сериализаторы
- services/ — S3-сервис
- alembic/ — миграции
- main.py — точка входа
