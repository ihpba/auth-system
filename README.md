# Система аутентификации и авторизации

Собственная реализация системы аутентификации (JWT) и авторизации (RBAC) на базе Django + DRF + PostgreSQL. Не использует встроенные механизмы аутентификации Django «из коробки» — все компоненты написаны с нуля.

---

## Схема базы данных

### ER-диаграмма

```
┌──────────────────┐       ┌──────────────────┐       ┌──────────────────┐
│  accounts_user   │       │  rbac_user_role  │       │    rbac_role      │
├──────────────────┤       ├──────────────────┤       ├──────────────────┤
│ id (UUID, PK)    │──┐    │ id (UUID, PK)    │    ┌──│ id (UUID, PK)    │
│ email (unique)   │  │    │ user_id (FK)     │────┘  │ codename (uniq)  │
│ password (hash)  │  └───>│ role_id (FK)     │───────│ name             │
│ first_name       │       └──────────────────┘       │ description      │
│ last_name        │                                   └───────┬──────────┘
│ patronymic       │                                           │
│ is_active        │                                           │ 1:N
│ created_at       │                                           ▼
│ updated_at       │       ┌──────────────────────────────────────────────┐
└──────────────────┘       │            rbac_permission                  │
                            ├──────────────────────────────────────────────┤
┌──────────────────────┐    │ id (UUID, PK)                               │
│accounts_refresh_token│    │ role_id (FK) ─────────> rbac_role            │
├──────────────────────┤    │ resource_id (FK) ──────> rbac_resource      │
│ id (UUID, PK)        │    │ action_id (FK) ────────> rbac_action        │
│ user_id (FK)         │    │ UNIQUE (role, resource, action)             │
│ token (unique)       │    └──────────────────────────────────────────────┘
│ expires_at           │                        │                │
│ is_revoked           │                        │                │
│ created_at           │           ┌────────────┘                │
└──────────────────────┘           │                             │
                                   ▼                             ▼
                        ┌──────────────────┐        ┌──────────────────┐
                        │  rbac_resource    │        │   rbac_action     │
                        ├──────────────────┤        ├──────────────────┤
                        │ id (UUID, PK)    │        │ id (UUID, PK)    │
                        │ codename (uniq)  │        │ codename (uniq)  │
                        │ name             │        │ name             │
                        │ description      │        └──────────────────┘
                        └──────────────────┘
```

### Описание таблиц

| Таблица | Назначение |
|---|---|
| `accounts_user` | Пользователи системы. Хранит email (логин), хеш пароля, ФИО, флаг `is_active` (мягкое удаление). Не наследуется от Django `AbstractUser`. |
| `accounts_refresh_token` | Refresh-токены для JWT-ротации. Позволяет отзывать токены при logout и мягком удалении. |
| `rbac_resource` | Ресурсы бизнес-приложения (например, «documents», «reports», «tasks»). Определяет **к чему** применяется правило доступа. |
| `rbac_action` | Действия над ресурсами (create, read, update, delete). Определяет **что** можно сделать. |
| `rbac_role` | Именованные наборы разрешений (admin, editor, viewer). Связующий элемент между пользователями и разрешениями. |
| `rbac_permission` | Связка «роль + ресурс + действие». Конкретное разрешение, назначаемое роли. |
| `rbac_user_role` | Назначение роли пользователю. Пользователь может иметь несколько ролей; итоговые права — объединение всех ролей. |

---

## Система разграничения прав доступа (RBAC)

### Принцип работы

Модель доступа — **RBAC (Role-Based Access Control)**:

```
Пользователь ──(UserRole)──> Роль ──(Permission)──> (Ресурс + Действие)
```

**Правила проверки при запросе к защищённому ресурсу:**

1. **Аутентификация** — система определяет пользователя по JWT-токену в заголовке `Authorization: Bearer <token>`.
   - Если токен отсутствует или невалиден → **401 Unauthorized**.
2. **Авторизация** — система проверяет, имеет ли пользователь разрешение на запрошенный (ресурс, действие).
   - Определяются все роли пользователя (таблица `rbac_user_role`).
   - Для каждой роли ищется разрешение в таблице `rbac_permission`, где `resource = <запрошенный_ресурс>` и `action = <запрошенное_действие>`.
   - Если хотя бы одна роль даёт нужное разрешение → **доступ разрешён**.
   - Если ни одна роль не даёт разрешения → **403 Forbidden**.

### Матрица доступа (тестовые данные)

| Ресурс | Действие | admin | editor | viewer | guest |
|--------|----------|:-----:|:------:|:------:|:-----:|
| documents | create  | + | + | - | - |
| documents | read    | + | + | + | - |
| documents | update  | + | + | - | - |
| documents | delete  | + | - | - | - |
| reports   | create  | + | - | - | - |
| reports   | read    | + | + | + | - |
| reports   | update  | + | - | - | - |
| reports   | delete  | + | - | - | - |
| tasks     | create  | + | + | - | - |
| tasks     | read    | + | + | + | - |
| tasks     | update  | + | + | - | - |
| tasks     | delete  | + | - | - | - |

### Аутентификация (JWT)

Система использует **собственную реализацию JWT** на базе библиотеки PyJWT (не djangorestframework-simplejwt):

- **Access-токен** (короткоживущий, 15 мин): содержит `sub` (user_id), `email`, `type=access`, `iat`, `exp`. Передаётся в заголовке `Authorization: Bearer <token>`.
- **Refresh-токен** (долгоживущий, 7 дней): содержит `sub`, `jti`, `type=refresh`, `iat`, `exp`. Хранится в БД (`accounts_refresh_token`) для возможности отзыва.
- **Login** → выдаётся пара (access + refresh).
- **Logout** → refresh-токен помечается `is_revoked=True`; access-токен остаётся действительным до истечения срока (stateless).
- **Rotation** — при обновлении access-токена старый refresh отзывается, выдаётся новая пара.
- **Мягкое удаление** — `is_active=False`, все refresh-токены отзываются, вход невозможен.

---

## API

### Аутентификация (`/api/auth/`)

| Метод | URL | Описание | Доступ |
|-------|-----|----------|--------|
| POST | `/api/auth/register/` | Регистрация | Публичный |
| POST | `/api/auth/login/` | Вход (получение JWT) | Публичный |
| POST | `/api/auth/logout/` | Выход (отзыв refresh) | Аутентифицированный |
| POST | `/api/auth/token/refresh/` | Обновление access-токена | Публичный |
| GET | `/api/auth/profile/` | Просмотр профиля | Аутентифицированный |
| PATCH | `/api/auth/profile/` | Обновление профиля | Аутентифицированный |
| POST | `/api/auth/profile/delete/` | Мягкое удаление аккаунта | Аутентифицированный |
| POST | `/api/auth/profile/change-password/` | Смена пароля | Аутентифицированный |

### RBAC — управление (`/api/rbac/`) — только для роли «admin»

| Метод | URL | Описание |
|-------|-----|----------|
| GET/POST | `/api/rbac/resources/` | Список / создание ресурсов |
| GET/PATCH/DELETE | `/api/rbac/resources/<id>/` | Чтение / обновление / удаление ресурса |
| GET/POST | `/api/rbac/actions/` | Список / создание действий |
| GET/PATCH/DELETE | `/api/rbac/actions/<id>/` | Чтение / обновление / удаление действия |
| GET/POST | `/api/rbac/roles/` | Список / создание ролей |
| GET/PATCH/DELETE | `/api/rbac/roles/<id>/` | Чтение / обновление / удаление роли |
| GET/POST | `/api/rbac/permissions/` | Список / создание разрешений |
| GET/DELETE | `/api/rbac/permissions/<id>/` | Чтение / удаление разрешения |
| GET/POST | `/api/rbac/user-roles/` | Список / назначение ролей |
| GET/DELETE | `/api/rbac/user-roles/<id>/` | Чтение / снятие роли |
| GET | `/api/rbac/users/<user_id>/permissions/` | Сводка разрешений пользователя |

### Бизнес-объекты (`/api/business/`) — с проверкой RBAC

| Метод | URL | Ресурс | Действие |
|-------|-----|--------|----------|
| GET | `/api/business/documents/` | documents | read |
| POST | `/api/business/documents/` | documents | create |
| PATCH | `/api/business/documents/<id>/` | documents | update |
| DELETE | `/api/business/documents/<id>/` | documents | delete |
| GET | `/api/business/reports/` | reports | read |
| POST | `/api/business/reports/` | reports | create |
| ... | (аналогично для tasks) | tasks | ... |

---

## Запуск проекта

### Через Docker Compose (рекомендуется)

```bash
docker-compose up -d
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py seed_data
```

### Локально (без Docker)

1. Установите PostgreSQL и создайте базу `auth_system`.
2. Создайте и активируйте виртуальное окружение:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```
3. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```
4. Скопируйте `.env.example` в `.env` и укажите параметры подключения к БД.
5. Выполните миграции и заполнение тестовыми данными:
   ```bash
   python manage.py migrate
   python manage.py seed_data
   ```
6. Запустите сервер:
   ```bash
   python manage.py runserver
   ```

### Swagger-документация

После запуска доступна по адресу: http://localhost:8000/api/docs/

---

## Тестирование

```bash
python manage.py test --verbosity=2
```

Тесты покрывают:
- Регистрацию (успех, дубликат email, несовпадение паролей, короткий пароль)
- Вход (успех, неверный пароль, несуществующий пользователь, деактивированный)
- Выход (успех, отзыв refresh-токена, без аутентификации)
- Профиль (просмотр, обновление, без аутентификации)
- Мягкое удаление (is_active=False, отзыв токенов, невозможность входа)
- Обновление токенов (успех, отозванный refresh)
- Смену пароля (успех, неверный старый, несовпадение новых)
- RBAC-разрешения (401 без токена, 403 без прав, 200 с правами)
- Admin-API RBAC (создание/чтение/удаление ролей, разрешений, назначений)
- Mock-View бизнес-объектов (возврат данных, 403 при отсутствии прав)

---

## Тестовые учётные данные

| Email | Пароль | Роль | Доступ |
|-------|--------|------|--------|
| admin@test.com | TestPass123! | admin | Полный доступ + управление RBAC |
| editor@test.com | TestPass123! | editor | Создание/чтение/обновление документов и задач; чтение отчётов |
| viewer@test.com | TestPass123! | viewer | Только чтение всех ресурсов |
| guest@test.com | TestPass123! | — | Нет доступа к бизнес-ресурсам (403) |

---

## Структура проекта

```
auth_system/
├── config/                    # Конфигурация Django-проекта
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── accounts/                  # Модуль аутентификации (пользователи, JWT)
│   ├── models.py              # CustomUser + CustomUserManager, RefreshToken
│   ├── authentication.py      # JWTAuthentication (DRF)
│   ├── middleware.py          # JWTAuthenticationMiddleware, AnonymousUser
│   ├── jwt_utils.py           # Генерация/валидация/отзыв токенов
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   ├── exceptions.py
│   ├── tests.py               # 28 тестов accounts
│   └── management/
│       └── commands/
│           └── seed_data.py   # Заполнение тестовыми данными
├── rbac/                      # Модуль авторизации (RBAC)
│   ├── models.py              # Resource, Action, Role, Permission, UserRole
│   ├── permissions.py         # RBACPermission (DRF)
│   ├── serializers.py
│   ├── views.py               # Admin API для управления RBAC
│   ├── urls.py
│   └── tests.py               # 9 тестов RBAC
├── business/                  # Mock-Views бизнес-объектов
│   ├── views.py               # DocumentViewSet, ReportViewSet, TaskViewSet
│   ├── urls.py
│   └── tests.py               # 4 теста бизнес-объектов
├── manage.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
└── .gitignore
```
