_______________________Архитектура_______________________

       ┌─────────────┐
       │     API     │
       │  (FastAPI)  │
       └─────┬───────┘
             │    
             v    
       ┌───────────── ───────┐
       │      PostsService   │
       └─┬──┬────────┬───────┘
        /   │        │      
       /    │        │      
      v     ↑        v      
┌──────────────┐ ┌─────────────┐
│ Repositories │ │ PostsCacheS │
│              │ │             │
└─────┬────────┘ └─────┬───────┘
      │                │   
      v                v    
   ┌──────────┐   ┌────────────────┐
   │   DB     │   │BaseCacheService│
   │(Postgres)│   │   (Redis)      │
   └──────────┘   └────────────────┘

В отличие от синглтона(на котором был реализован первый вариант)
Данный подход выбран с соображениями будущего масштабирования, удобства управлением кешированием сервисов 
по отдельности, простотой замены Redis на что-то иное, легче тестировать (замокать). 
Также позволяет применять зависимость только в тех сервисах, где это необходимо, а не тянуть во все
соблюдение SRP и ISP

RedisManager - транспортный уровень, BaseCacheService - низкоуровневый, 
PostsCacheService - высокоуровневый для реализации логики кеширования конкретного сервиса


Из особенностей - Используется Handler для автоматического отлова ошибок и проброса кастомных исключений

Заглушка авторизации (в dependencies)


____________________________Структура____________________________

├── .secrets
|         ├── .db
│         └── .env
|
└── blog_service
    |
    ├── scripts
    │         └── seeds.py
    ├── src
    │     ├── api
    │         ├── api.py
    │                   └── dependencies.py
    │         ├── config.py
    │         ├── connectors
    │         ├── database.py
    │         │         └── redis_client.py
    │         ├── exceptions
    │         │         ├── exceptions_handlers.py
    │         │         └── exceptions.py
    │         ├── main.py
    │         ├── migrations
    │         │         ├── env.py
    │         │         ├── __init__.py
    │         │         ├── README
    │         │         ├── script.py.mako
    │         │         └── versions
    │         ├── models
    │         │         ├── __init__.py
    │         │         ├── posts.py
    │         │         └── users.py
    │         ├── repositories
    │         │         ├── base.py
    │         │         ├── posts.py
    │         │         └── users.py
    │         ├── schemas
    │         ├── post_schemas.py
    │         │         └── users.py
    │         ├── services
    │         │         ├── base.py
    │         │         ├── cache
    │         │         │         ├── cache_service.py
    │         │         │         └── posts_cache.py
    │         │         └── posts_services.py
    │         └── utils
    │             ├── db_manager.py
    │             └── rate_limiter.py
    ├── tests
    │         ├── conftest.py
    │         ├── integration
    │         └── unit
    │         └── services
    │                 ├── postcache
    │                 └── post_service
    |
    ├── alembic.ini
    ├── docker-compose.dev.yml
    ├── docker-compose.prod.yml
    ├── Dockerfile.dev
    ├── Dockerfile.prod
    ├── logger.py
    ├── pyproject.toml
    ├── pytest.ini
    ├── README.md
    └── uv.lock


____________________________Требования____________________________
uv (astral-UV) пакетный менеджер
docker

____________________________Запуск____________________________

1. В папке лежат примеры секреток - переименовать examples (должны остаться .db и .env)
(вынесены они вне сервиса, что бы не попадали внутрь кода контейнера при монтировании)

На проекте 2 docker-compose файла - для разработки (dev) с наличием hot-reload, volumes и (prod) с доп настройками 
по безопасности

2. Запуск на выбор режима:

- docker compose -f docker-compose.dev.yml up -d --build
- docker compose -f docker-compose.prod.yml up -d --build 


Миграции проходят автоматически в контейнере

3. Для удобства проверки в режиме dev при первом запуске БД идет автозаполнение данными, пользователи и посты

4. Доступ к документации стандартный http://localhost:8000/docs



___________________________Тестирование___________________________
Используется Pytest

Сперва подтягиваем зависимости при помощи uv:
- находясь в папке blog_service выполняем -  uv sync
- uv run pytest .



Либо:
- после uv sync переключаемся на виртуальное окружение source .venv/bin/activate
-  pytest .



Запуск стандартный  из папки posts_service   pytest . (-v -s)

_____________________Комментарий_____________________

 - Ручка get_all_posts оставлена для наглядности, в ней нет кеширования и сортировки
 - Заглушка авторизации по умолчанию возвращает пользователя с user_id = 1


