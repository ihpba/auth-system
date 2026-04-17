# Python с нуля до джуна: Путь к созданию системы аутентификации

> Учебник, который шаг за шагом ведёт от основ Python
> к пониманию каждого файла проекта auth-system.

---

## Содержание

1. [Основы Python](#1-основы-python)
2. [Структуры данных](#2-структуры-данных)
3. [Функции и модули](#3-функции-и-модули)
4. [ООП — классы и объекты](#4-ооп--классы-и-объекты)
5. [Обработка ошибок](#5-обработка-ошибок)
6. [Работа с файлами и JSON](#6-работа-с-файлами-и-json)
7. [HTTP и REST API](#7-http-и-rest-api)
8. [Django — основы](#8-django--основы)
9. [Django ORM — модели и БД](#9-django-orm--модели-и-бд)
10. [Django REST Framework](#10-django-rest-framework)
11. [JWT-аутентификация](#11-jwt-аутентификация)
12. [RBAC — система авторизации](#12-rbac--система-авторизации)
13. [Собираем всё вместе: разбор проекта](#13-собираем-всё-вместе-разбор-проекта)

---

## 1. Основы Python

### 1.1 Переменные и типы данных

Python — язык с динамической типизацией. Тип переменной определяется автоматически.

```python
# Числа
age = 25              # int (целое число)
price = 99.99         # float (дробное число)

# Строки
name = "Анна"         # str (строка)

# Логический тип
is_active = True      # bool (True / False)

# None — «пустое» значение
middle_name = None    # NoneType

# Можно узнать тип:
print(type(age))      # <class 'int'>
```

### 1.2 Операции

```python
# Арифметика
x = 10 + 3    # 13
x = 10 - 3    # 7
x = 10 * 3    # 30
x = 10 / 3    # 3.333...  (всегда float)
x = 10 // 3   # 3   (целочисленное деление)
x = 10 % 3    # 1   (остаток)
x = 2 ** 10   # 1024 (степень)

# Сравнения — возвращают bool
10 == 10    # True   (равно)
10 != 5     # True   (не равно)
10 > 5      # True
10 < 5      # False
10 >= 10    # True
10 <= 9     # False

# Логические операции
True and False   # False  (И)
True or False    # True   (ИЛИ)
not True         # False  (НЕ)
```

### 1.3 Строки

```python
# Форматирование f-строками (самый удобный способ)
name = "Анна"
age = 25
print(f"Привет, {name}! Тебе {age} лет.")

# Полезные методы строк
email = "  User@Mail.COM  "
email.strip()          # "User@Mail.COM"  — убрать пробелы
email.strip().lower()  # "user@mail.com"  — привести к нижнему регистру

"hello".replace("l", "L")   # "heLLo"
"text".startswith("te")     # True
"user@mail.com".endswith(".com")  # True
"user@mail.com".split("@")       # ["user", "mail.com"]
":".join(["a", "b", "c"])        # "a:b:c"
len("hello")                     # 5
```

### 1.4 Условия

```python
age = 17

if age >= 18:
    print("Доступ разрешён")
elif age >= 14:
    print("Доступ ограничен")
else:
    print("Доступ запрещён")

# Тернарный оператор
status = "взрослый" if age >= 18 else "ребёнок"
```

### 1.5 Циклы

```python
# for — перебор элементов
fruits = ["яблоко", "банан", "вишня"]
for fruit in fruits:
    print(fruit)

# range(start, stop, step) — генерация чисел
for i in range(5):       # 0, 1, 2, 3, 4
    print(i)

for i in range(2, 10, 3):  # 2, 5, 8
    print(i)

# while — цикл с условием
count = 0
while count < 3:
    print(count)
    count += 1

# break и continue
for i in range(10):
    if i == 3:
        continue    # пропустить итерацию
    if i == 7:
        break       # выйти из цикла
    print(i)        # 0, 1, 2, 4, 5, 6
```

---

## 2. Структуры данных

### 2.1 Списки (list)

Список — упорядоченная изменяемая коллекция.

```python
# Создание
numbers = [1, 2, 3, 4, 5]
mixed = [1, "text", True, 3.14]
empty = []

# Доступ по индексу (с нуля!)
numbers[0]     # 1
numbers[-1]    # 5  (последний элемент)

# Срезы (slices)
numbers[1:4]   # [2, 3, 4]
numbers[:3]    # [1, 2, 3]
numbers[2:]    # [3, 4, 5]
numbers[::2]   # [1, 3, 5]  (каждый второй)

# Изменение
numbers.append(6)          # [1,2,3,4,5,6] — добавить в конец
numbers.insert(0, 0)       # [0,1,2,3,4,5,6] — вставить по индексу
numbers.pop()              # удалить последний → вернёт 6
numbers.remove(3)          # удалить значение 3
numbers.sort()             # отсортировать на месте
sorted(numbers)            # вернуть новый отсортированный список

# Проверка
3 in numbers               # True
len(numbers)               # длина списка
```

### 2.2 Словари (dict)

Словарь — коллекция пар «ключ: значение».

```python
# Создание
user = {
    "email": "test@mail.com",
    "age": 25,
    "is_active": True,
}

# Доступ
user["email"]              # "test@mail.com"
user.get("name", "нет")    # "нет" — значение по умолчанию, если ключа нет

# Изменение
user["name"] = "Анна"      # добавить/обновить ключ
user.pop("age")            # удалить ключ → вернёт 25

# Проверка
"email" in user            # True
user.keys()                # dict_keys(["email", "is_active", "name"])
user.values()              # dict_values(["test@mail.com", True, "Анна"])
user.items()               # пары (ключ, значение)

# Перебор
for key, value in user.items():
    print(f"{key}: {value}")
```

### 2.3 Кортежи (tuple)

Кортеж — неизменяемый список.

```python
coords = (10, 20)
coords[0]        # 10
# coords[0] = 5  # ОШИБКА! Кортеж неизменяем

# Распаковка
x, y = coords    # x=10, y=20
```

### 2.4 Множества (set)

Множество — коллекция уникальных элементов.

```python
unique = {1, 2, 3, 3, 3}    # {1, 2, 3} — дубликаты удалены
unique.add(4)
unique.discard(2)

set_a = {1, 2, 3}
set_b = {3, 4, 5}
set_a & set_b                # {3}        — пересечение
set_a | set_b                # {1,2,3,4,5} — объединение
set_a - set_b                # {1, 2}     — разность
```

### 2.5 Генераторы списков и словарей (comprehensions)

```python
# List comprehension
squares = [x ** 2 for x in range(10)]
# [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]

# С условием
evens = [x for x in range(20) if x % 2 == 0]
# [0, 2, 4, 6, 8, 10, 12, 14, 16, 18]

# Dict comprehension
word_lengths = {word: len(word) for word in ["hello", "world"]}
# {"hello": 5, "world": 5}
```

---

## 3. Функции и модули

### 3.1 Функции

```python
# Простая функция
def greet(name):
    return f"Привет, {name}!"

result = greet("Анна")  # "Привет, Анна!"

# Параметры по умолчанию
def create_user(email, is_active=True):
    return {"email": email, "is_active": is_active}

create_user("a@b.com")            # is_active=True
create_user("a@b.com", False)     # is_active=False

# Именованные аргументы
create_user(email="a@b.com", is_active=False)

# *args и **kwargs — произвольное число аргументов
def total(*numbers):
    return sum(numbers)

total(1, 2, 3)  # 6

def print_info(**kwargs):
    for key, value in kwargs.items():
        print(f"{key} = {value}")

print_info(name="Анна", age=25)

# Аннотации типов (подсказки, не обязательны)
def add(a: int, b: int) -> int:
    return a + b
```

### 3.2 Лямбда-функции

```python
# Однострочная безымянная функция
square = lambda x: x ** 2
square(5)  # 25

# Часто используется с sorted, map, filter
users = [{"name": "Борис", "age": 30}, {"name": "Анна", "age": 25}]
sorted(users, key=lambda u: u["age"])
# [{"name": "Анна", ...}, {"name": "Борис", ...}]
```

### 3.3 Модули и импорты

```python
# Импорт модуля целиком
import os
os.getcwd()            # текущая директория

# Импорт конкретной функции
from datetime import datetime
datetime.now()         # текущее время

# Импорт с псевдонимом
import numpy as np

# Свой модуль — файл my_utils.py:
def double(x):
    return x * 2

# В другом файле:
from my_utils import double
double(5)  # 10
```

### 3.4 Декораторы

Декоратор — функция, которая «оборачивает» другую функцию, расширяя её поведение.

```python
def timer(func):
    """Декоратор, замеряющий время выполнения."""
    import time
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start
        print(f"{func.__name__} выполнялась {elapsed:.3f}с")
        return result
    return wrapper

@timer
def slow_function():
    import time
    time.sleep(1)
    return "готово"

slow_function()  # slow_function выполнялась 1.001с
```

---

## 4. ООП — классы и объекты

ООП — парадигма, на которой построен Django. Это **обязательная** тема.

### 4.1 Класс и объект

```python
class User:
    """Класс — чертёж объекта. Объект — конкретный экземпляр."""

    # Атрибут класса (общий для всех объектов)
    species = "Homo sapiens"

    # __init__ — конструктор (вызывается при создании объекта)
    def __init__(self, email: str, age: int):
        # self — ссылка на текущий объект
        self.email = email      # атрибут экземпляра
        self.age = age
        self.is_active = True   # значение по умолчанию

    # Метод экземпляра
    def greet(self) -> str:
        return f"Я {self.email}, мне {self.age} лет"

    def deactivate(self):
        self.is_active = False


# Создание объектов
user1 = User("anna@mail.com", 25)
user2 = User("boris@mail.com", 30)

print(user1.email)        # anna@mail.com
print(user1.greet())      # Я anna@mail.com, мне 25 лет
print(user1.is_active)    # True
user1.deactivate()
print(user1.is_active)    # False
```

### 4.2 Наследование

```python
class Animal:
    def __init__(self, name):
        self.name = name

    def speak(self):
        raise NotImplementedError("Подкласс должен реализовать speak()")


class Dog(Animal):
    def speak(self):
        return f"{self.name} говорит: Гав!"


class Cat(Animal):
    def speak(self):
        return f"{self.name} говорит: Мяу!"


dog = Dog("Рекс")
cat = Cat("Мурка")
dog.speak()  # Рекс говорит: Гав!
cat.speak()  # Мурка говорит: Мяу!
```

### 4.3 Магические методы (dunder-методы)

```python
class Money:
    def __init__(self, amount: float, currency: str = "RUB"):
        self.amount = amount
        self.currency = currency

    def __str__(self):
        """Человекочитаемое представление (print, str())."""
        return f"{self.amount:.2f} {self.currency}"

    def __repr__(self):
        """Представление для разработчика (repr(), отладка)."""
        return f"Money({self.amount}, '{self.currency}')"

    def __eq__(self, other):
        """Равенство (==)."""
        return self.amount == other.amount and self.currency == other.currency

    def __add__(self, other):
        """Сложение (+)."""
        if self.currency != other.currency:
            raise ValueError("Разные валюты!")
        return Money(self.amount + other.amount, self.currency)

    def __bool__(self):
        """Логическое значение (if money:)."""
        return self.amount > 0


price = Money(100)
tax = Money(20)
total = price + tax     # Money(120)
print(total)            # 120.00 RUB
if total:               # True (amount > 0)
    print("Сумма ненулевая")
```

### 4.4 Свойства (property)

```python
class Temperature:
    def __init__(self, celsius: float):
        self._celsius = celsius   # _ — соглашение: «приватный» атрибут

    @property
    def celsius(self):
        """Геттер — чтение."""
        return self._celsius

    @celsius.setter
    def celsius(self, value):
        """Сеттер — запись с валидацией."""
        if value < -273.15:
            raise ValueError("Ниже абсолютного нуля!")
        self._celsius = value

    @property
    def fahrenheit(self):
        """Вычисляемое свойство (только чтение)."""
        return self._celsius * 9 / 5 + 32


temp = Temperature(25)
print(temp.fahrenheit)    # 77.0 — вычисляется на лету
temp.celsius = 30        # OK
# temp.celsius = -300    # ОШИБКА: ValueError
```

### 4.5 Класс-методы и статические методы

```python
class User:
    def __init__(self, email: str, password_hash: str):
        self.email = email
        self.password_hash = password_hash

    @classmethod
    def from_plain_password(cls, email: str, raw_password: str):
        """Альтернативный конструктор — создаёт объект из открытого пароля."""
        import hashlib
        hashed = hashlib.sha256(raw_password.encode()).hexdigest()
        return cls(email=email, password_hash=hashed)

    @staticmethod
    def is_valid_email(email: str) -> bool:
        """Утилитный метод — не зависит от экземпляра."""
        return "@" in email and "." in email.split("@")[-1]


# Через обычный конструктор
user1 = User("a@b.com", "abc123hash")

# Через альтернативный конструктор
user2 = User.from_plain_password("a@b.com", "mypassword")

User.is_valid_email("test@mail.com")  # True
```

---

## 5. Обработка ошибок

### 5.1 try / except

```python
def divide(a, b):
    try:
        result = a / b
    except ZeroDivisionError:
        print("Деление на ноль!")
        return None
    except TypeError:
        print("Неверный тип аргументов!")
        return None
    else:
        # Выполняется, если исключения НЕ было
        print("Всё OK")
        return result
    finally:
        # Выполняется ВСЕГДА (было исключение или нет)
        print("Блок finally")


divide(10, 2)    # Всё OK → 5.0 → блок finally
divide(10, 0)    # Деление на ноль! → None → блок finally
```

### 5.2 Создание своих исключений

```python
class AuthenticationError(Exception):
    """Пользователь не аутентифицирован."""
    pass


class AuthorizationError(Exception):
    """Пользователь не авторизован (нет прав)."""
    pass


def check_access(user, resource):
    if user is None:
        raise AuthenticationError("Пользователь не определён")
    if not user.has_permission(resource):
        raise AuthorizationError(f"Доступ к {resource} запрещён")
    return True


# Использование
try:
    check_access(user=None, resource="documents")
except AuthenticationError:
    print("401 Unauthorized")
except AuthorizationError:
    print("403 Forbidden")
```

---

## 6. Работа с файлами и JSON

### 6.1 Чтение и запись файлов

```python
# Запись
with open("data.txt", "w", encoding="utf-8") as f:
    f.write("Первая строка\n")
    f.write("Вторая строка\n")
# with автоматически закрывает файл

# Чтение
with open("data.txt", "r", encoding="utf-8") as f:
    content = f.read()          # весь файл одной строкой

with open("data.txt", "r", encoding="utf-8") as f:
    lines = f.readlines()       # список строк

with open("data.txt", "r", encoding="utf-8") as f:
    for line in f:              # построчное чтение (экономит память)
        print(line.strip())
```

### 6.2 JSON

```python
import json

data = {
    "users": [
        {"email": "a@b.com", "age": 25},
        {"email": "c@d.com", "age": 30},
    ]
}

# Сериализация: Python → JSON-строка
json_string = json.dumps(data, ensure_ascii=False, indent=2)

# Запись в файл
with open("data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

# Чтение из файла
with open("data.json", "r", encoding="utf-8") as f:
    loaded = json.load(f)

# Десериализация: JSON-строка → Python
parsed = json.loads('{"email": "a@b.com"}')
```

---

## 7. HTTP и REST API

### 7.1 Что такое HTTP

HTTP — протокол общения клиента (браузер, приложение) и сервера.

**Запрос** состоит из:
- **Метод** — что хотим сделать (GET, POST, PATCH, DELETE)
- **URL** — путь к ресурсу (`/api/users/`)
- **Заголовки** — метаданные (`Authorization: Bearer <token>`)
- **Тело** — данные (JSON при POST/PATCH)

**Ответ** состоит из:
- **Статус-код** — результат (200 OK, 201 Created, 401 Unauthorized, 403 Forbidden, 404 Not Found)
- **Заголовки**
- **Тело** — данные (обычно JSON)

### 7.2 REST — принципы проектирования API

| Метод   | URL              | Действие          | Статус |
|---------|------------------|-------------------|--------|
| GET     | /api/users/      | Получить список   | 200    |
| POST    | /api/users/      | Создать нового    | 201    |
| GET     | /api/users/1/    | Получить одного   | 200    |
| PATCH   | /api/users/1/    | Обновить частично | 200    |
| DELETE  | /api/users/1/    | Удалить           | 204    |

### 7.3 Пример запроса (curl)

```bash
# Регистрация
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@mail.com","password":"Pass1234!","password_confirm":"Pass1234!","first_name":"Иван","last_name":"Иванов"}'

# Логин
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@mail.com","password":"Pass1234!"}'

# Запрос с токеном (Authenticated)
curl http://localhost:8000/api/auth/profile/ \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

## 8. Django — основы

### 8.1 Что такое Django

Django — фреймворк для создания веб-приложений на Python.
Он обрабатывает HTTP-запросы и возвращает HTTP-ответы.

**MVT-архитектура:**
- **Model** (Модель) — работа с данными (БД)
- **View** (Представление) — логика обработки запросов
- **Template** (Шаблон) — отображение (в нашем API-проекте не используем)

### 8.2 Жизненный цикл запроса в Django

```
Клиент → HTTP-запрос
  → Middleware (промежуточные слои — аутентификация, логирование)
  → URL-роутер (определяет, какая View обработает запрос)
  → View (логика: проверить данные, обратиться к модели, сформировать ответ)
  → HTTP-ответ → Клиент
```

### 8.3 Структура проекта

```
auth_system/             # Корень проекта
├── manage.py            # Утилита управления Django
├── config/              # Настройки проекта
│   ├── settings.py      # Конфигурация (БД, приложения, middleware)
│   ├── urls.py          # Корневые URL-маршруты
│   └── wsgi.py          # Точка входа для production-сервера
├── accounts/            # Приложение «пользователи»
│   ├── models.py        # Модели (таблицы БД)
│   ├── views.py         # Представления (обработчики запросов)
│   ├── urls.py          # URL-маршруты приложения
│   └── serializers.py   # Сериализаторы (валидация/форматирование данных)
└── rbac/                # Приложение «авторизация»
    └── ...
```

### 8.4 settings.py — конфигурация

```python
# Секретный ключ для подписи cookies, JWT и др.
SECRET_KEY = "длинный-случайный-ключ"

# Режим отладки (True при разработке, False в production)
DEBUG = True

# Какие хосты обслуживать
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

# Установленные приложения — модули проекта
INSTALLED_APPS = [
    "django.contrib.contenttypes",  # встроенный: типы контента
    "rest_framework",               # DRF — наш главный инструмент
    "accounts",                     # наше приложение
    "rbac",                         # наше приложение
]

# Промежуточные слои — обрабатывают каждый запрос/ответ
MIDDLEWARE = [
    "django.middleware.common.CommonMiddleware",
    "accounts.middleware.JWTAuthenticationMiddleware",  # наш!
]

# Подключение к базе данных
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "auth_system",
        "USER": "postgres",
        "PASSWORD": "password",
        "HOST": "localhost",
        "PORT": "5432",
    }
}
```

### 8.5 URLs — маршрутизация

```python
# config/urls.py — корневой файл маршрутов
from django.urls import path, include

urlpatterns = [
    path("api/auth/", include("accounts.urls")),    # делегируем accounts
    path("api/rbac/", include("rbac.urls")),         # делегируем rbac
]

# accounts/urls.py — маршруты приложения
from django.urls import path
from accounts.views import RegisterView, LoginView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="auth-register"),
    path("login/", LoginView.as_view(), name="auth-login"),
]
# Итоговый URL: /api/auth/register/
```

### 8.6 Views — обработчики запросов

```python
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class HelloView(APIView):
    """Простейшее представление."""

    def get(self, request):
        """Обработка GET-запроса."""
        return Response({"message": "Привет!"})

    def post(self, request):
        """Обработка POST-запроса."""
        name = request.data.get("name")
        if not name:
            return Response(
                {"detail": "Имя обязательно."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            {"message": f"Привет, {name}!"},
            status=status.HTTP_201_CREATED,
        )
```

---

## 9. Django ORM — модели и БД

### 9.1 Модель — описание таблицы в БД

```python
from django.db import models

class User(models.Model):
    # Каждое поле модели → колонка в таблице
    email = models.EmailField(unique=True)     # VARCHAR с проверкой email
    password = models.CharField(max_length=128) # хеш пароля
    first_name = models.CharField(max_length=150)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)  # при создании
    updated_at = models.DateTimeField(auto_now=True)       # при каждом save()

    class Meta:
        db_table = "users"  # имя таблицы в БД
```

### 9.2 Типы полей

| Тип поля          | Python-тип  | SQL-тип      | Описание                  |
|-------------------|-------------|--------------|---------------------------|
| CharField         | str         | VARCHAR(n)   | Строка ограниченной длины |
| TextField         | str         | TEXT         | Длинный текст             |
| EmailField        | str         | VARCHAR      | Email (с валидацией)      |
| BooleanField      | bool        | BOOLEAN      | True/False                |
| IntegerField      | int         | INTEGER      | Целое число               |
| FloatField        | float       | FLOAT        | Дробное число             |
| UUIDField         | UUID        | UUID         | Уникальный идентификатор  |
| DateTimeField     | datetime    | TIMESTAMP    | Дата и время              |
| ForeignKey        | объект      | INTEGER + FK | Внешний ключ (связь M:1)  |
| ManyToManyField   | QuerySet    | Таблица связи| Связь M:N                |
| SlugField         | str         | VARCHAR      | URL-безопасная строка     |

### 9.3 Связи между моделями

```python
class Author(models.Model):
    name = models.CharField(max_length=100)


class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.ForeignKey(
        Author,                     # связанная модель
        on_delete=models.CASCADE,   # при удалении автора → удалить книги
        related_name="books",       # обратная ссылка: author.books.all()
    )


class Tag(models.Model):
    name = models.CharField(max_length=50)


class Article(models.Model):
    title = models.CharField(max_length=200)
    tags = models.ManyToManyField(Tag, related_name="articles")
    # Создаёт промежуточную таблицу article_tags
```

### 9.4 ORM-запросы (QuerySet)

```python
# CREATE
user = User.objects.create(email="a@b.com", password="hash123")

# READ
User.objects.all()                            # все записи
User.objects.get(email="a@b.com")             # одна (или DoesNotExist)
User.objects.filter(is_active=True)           # фильтрация
User.objects.filter(email__endswith="@mail.com")  # __endswith — lookup
User.objects.filter(age__gte=18)                  # __gte — больше или равно
User.objects.first()                          # первый или None
User.objects.count()                          # количество

# UPDATE
user.email = "new@b.com"
user.save()                                   # сохранить изменения
User.objects.filter(is_active=False).update(is_active=True)  # массово

# DELETE
user.delete()                                 # удалить из БД

# Lookup-выражения (фильтры)
# __exact, __iexact, __contains, __icontains,
# __startswith, __endswith, __gt, __gte, __lt, __lte,
# __in, __isnull
User.objects.filter(email__in=["a@b.com", "c@d.com"])
User.objects.filter(patronymic__isnull=True)

# Связанные объекты
author = Author.objects.get(name="Пушкин")
author.books.all()                            # все книги автора

# values_list — получить только определённые поля
User.objects.values_list("email", flat=True)  # ["a@b.com", "c@d.com"]
```

### 9.5 Миграции

Миграции — способ применять изменения моделей к реальной БД.

```bash
python manage.py makemigrations   # создать файл миграции из моделей
python manage.py migrate          # применить миграции к БД
python manage.py showmigrations   # показать статус миграций
```

---

## 10. Django REST Framework

### 10.1 Что такое DRF

DRF — расширение Django для создания REST API.
Главные компоненты:
- **Сериализаторы** — валидация входных данных + форматирование выходных
- **Представления** — обработка HTTP-запросов
- **Права доступа (Permissions)** — кто может обратиться к эндпоинту

### 10.2 Сериализаторы

```python
from rest_framework import serializers

# Вариант 1: ModelSerializer (автоматически по модели)
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ("id", "email", "first_name", "last_name", "is_active")
        read_only_fields = ("id", "is_active")  # нельзя менять через API

# Вариант 2: Serializer (ручное описание полей — полная свобода)
class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)

    def validate_email(self, value):
        """Валидация одного поля."""
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("Такой email уже зарегистрирован.")
        return value.lower()

    def validate(self, data):
        """Валидация нескольких полей вместе."""
        if data["password"] != data["password_confirm"]:
            raise serializers.ValidationError({"password_confirm": "Пароли не совпадают."})
        return data

    def create(self, validated_data):
        """Создание объекта из валидированных данных."""
        validated_data.pop("password_confirm")
        raw_password = validated_data.pop("password")
        user = CustomUser(**validated_data)
        user.set_password(raw_password)
        user.save()
        return user
```

### 10.3 Представления (Views)

```python
# APIView — максимальный контроль
class LoginView(APIView):
    permission_classes = [AllowAny]  # доступен без токена

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        user = CustomUser.objects.filter(email=email).first()
        if not user or not user.check_password(password):
            return Response(
                {"detail": "Неверный email или пароль."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        return Response({"email": user.email})


# Generics — готовые операции CRUD
class UserListView(generics.ListCreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
```

### 10.4 Permissions — права доступа

```python
from rest_framework.permissions import BasePermission

class IsAdmin(BasePermission):
    """Доступ только для пользователей с ролью admin."""

    message = "Требуется роль администратора."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return UserRole.objects.filter(
            user=request.user, role__codename="admin"
        ).exists()
```

### 10.5 Аутентификация в DRF

DRF вызывает `authenticate()` для каждого запроса.
Результат помещается в `request.user` и `request.auth`.

```python
from rest_framework import authentication, exceptions

class JWTAuthentication(authentication.BaseAuthentication):
    """Собственная аутентификация по JWT."""

    def authenticate(self, request):
        # 1. Извлечь токен из заголовка
        auth_header = request.META.get("HTTP_AUTHORIZATION", "")
        if not auth_header.startswith("Bearer "):
            return None  # передать следующему authentication-классу

        token = auth_header.split(" ")[1]

        # 2. Декодировать токен
        try:
            payload = decode_token(token)
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed("Токен истёк.")

        # 3. Найти пользователя
        user = CustomUser.objects.get(id=payload["sub"], is_active=True)

        # 4. Вернуть кортеж (user, payload)
        return (user, payload)
```

---

## 11. JWT-аутентификация

### 11.1 Что такое JWT

JWT (JSON Web Token) — стандарт RFC 7519. Это строка вида:

```
eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0In0.abc123signature
```

Состоит из трёх частей, разделённых точкой:
1. **Header** (алгоритм подписи) — `{"alg": "HS256"}`
2. **Payload** (полезные данные) — `{"sub": "user_id", "exp": 1713000000}`
3. **Signature** (подпись) — HMAC-SHA256(header + payload, secret_key)

### 11.2 Зачем два токена

| Токен    | Срок     | Где хранится          | Назначение                |
|----------|----------|-----------------------|---------------------------|
| Access   | 15 мин   | В памяти клиента      | Аутентификация запросов   |
| Refresh  | 7 дней   | В БД + httpOnly cookie | Обновление access-токена  |

**Почему так:** access-токен короткоживущий — если его украдут, он скоро протухнет.
Refresh хранится в БД — его можно отозвать при logout.

### 11.3 Генерация JWT (PyJWT)

```python
import jwt
from datetime import datetime, timedelta, timezone

SECRET_KEY = "my-secret-key"
ALGORITHM = "HS256"

def generate_access_token(user) -> str:
    """Создаёт access-токен."""
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user.id),         # subject — идентификатор пользователя
        "email": user.email,          # дополнительное поле
        "type": "access",             # тип токена (для различения)
        "iat": now,                   # issued at — время выдачи
        "exp": now + timedelta(minutes=15),  # expiration — время истечения
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str) -> dict:
    """Декодирует и верифицирует токен."""
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

# Проверка
token = generate_access_token(user)
payload = decode_token(token)
print(payload["sub"])   # идентификатор пользователя
```

### 11.4 Схема login / logout / refresh

```
┌──────────┐                          ┌──────────┐
│  Клиент   │                          │  Сервер   │
└────┬─────┘                          └────┬─────┘
     │  POST /login/ {email, password}    │
     │────────────────────────────────────>│
     │                                     │ 1. Проверить email/password
     │                                     │ 2. Создать access + refresh
     │  {access: "...", refresh: "..."}    │ 3. Сохранить refresh в БД
     │<────────────────────────────────────│
     │                                     │
     │  GET /profile/                      │
     │  Authorization: Bearer <access>     │
     │────────────────────────────────────>│
     │                                     │ 4. Декодировать access
     │  {email: "...", ...}                │ 5. Найти пользователя
     │<────────────────────────────────────│
     │                                     │
     │  POST /token/refresh/ {refresh}     │
     │────────────────────────────────────>│
     │                                     │ 6. Проверить refresh в БД
     │  {access: "новый", refresh: "новый"}│ 7. Отозвать старый refresh
     │<────────────────────────────────────│ 8. Выдать новую пару
     │                                     │
     │  POST /logout/ {refresh}            │
     │────────────────────────────────────>│
     │                                     │ 9. Пометить refresh как revoked
     │  {"detail": "Вы вышли"}             │
     │<────────────────────────────────────│
```

---

## 12. RBAC — система авторизации

### 12.1 Что такое RBAC

RBAC (Role-Based Access Control) — модель доступа через роли.

```
Пользователь ──(UserRole)──> Роль ──(Permission)──> (Ресурс + Действие)
```

### 12.2 Пример проверки прав

```python
def user_has_permission(user, resource: str, action: str) -> bool:
    """
    Проверяет, имеет ли пользователь разрешение.

    1. Найти все роли пользователя.
    2. Проверить, есть ли у хотя бы одной роли
       разрешение на (ресурс, действие).
    """
    user_role_ids = UserRole.objects.filter(
        user=user
    ).values_list("role_id", flat=True)

    return Permission.objects.filter(
        role_id__in=user_role_ids,
        resource__codename=resource,
        action__codename=action,
    ).exists()


# Пример: может ли admin читать документы?
user_has_permission(admin_user, "documents", "read")   # True
user_has_permission(viewer_user, "documents", "create")  # False
user_has_permission(guest_user, "documents", "read")     # False
```

### 12.3 RBACPermission для DRF

```python
class RBACPermission(BasePermission):
    """
    Проверяет права на основе rbac_resource и rbac_action_map
    атрибутов View/ViewSet.
    """

    def has_permission(self, request, view):
        # Неаутентифицированный → False → DRF вернёт 401
        if not request.user or not request.user.is_authenticated:
            return False

        # Какой ресурс проверяем?
        resource = getattr(view, "rbac_resource", None)
        if resource is None:
            return True  # ресурс не указан — доступ открыт

        # Какое действие соответствует HTTP-методу?
        action_map = getattr(view, "rbac_action_map", {})
        action = action_map.get(request.method.lower())
        if action is None:
            return False  # метод не описан → запрет

        # Проверка в БД
        return user_has_permission(request.user, resource, action)


# Использование в ViewSet:
class DocumentViewSet(viewsets.ViewSet):
    rbac_resource = "documents"
    rbac_action_map = {
        "get": "read",
        "post": "create",
        "patch": "update",
        "delete": "delete",
    }
    permission_classes = [IsAuthenticated, RBACPermission]
```

---

## 13. Собираем всё вместе: разбор проекта

Теперь разберём каждый файл проекта auth-system,
связывая его с изученными концепциями.

### 13.1 accounts/models.py

```python
# Модель CustomUser — НЕ наследует AbstractUser из Django
# (задание: «не из коробки»)
class CustomUser(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    email = models.EmailField(unique=True, db_index=True)
    password = models.CharField(max_length=128)      # хеш, не открытый пароль!
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    patronymic = models.CharField(max_length=150, blank=True, default="")
    is_active = models.BooleanField(default=True)    # мягкое удаление
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = CustomUserManager()  # чтобы работал create_user()

    @property                                          # ← Свойство (раздел 4.4)
    def is_authenticated(self) -> bool:
        return True  # DRF проверяет: if user.is_authenticated

    def set_password(self, raw_password: str):
        self.password = make_password(raw_password)    # хеширование

    def check_password(self, raw_password: str) -> bool:
        return check_password(raw_password, self.password)
```

### 13.2 accounts/jwt_utils.py

```python
# Генерация и валидация JWT (раздел 11.3)
def generate_access_token(user) -> str:
    payload = {
        "sub": str(user.id),
        "type": "access",
        "iat": now(),
        "exp": now() + settings.JWT_ACCESS_LIFETIME,
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, settings.JWT_ALGORITHM)

def generate_refresh_token(user) -> tuple[str, datetime]:
    payload = {"sub": str(user.id), "jti": str(uuid4()), "type": "refresh", ...}
    token_str = jwt.encode(payload, ...)
    RefreshToken.objects.create(user=user, token=token_str, ...)  # ← ORM (9.4)
    return token_str, expires_at
```

### 13.3 accounts/views.py

```python
# Каждая View — обработчик HTTP-запроса (разделы 8.6, 10.3)
class LoginView(APIView):           # ← Наследование (4.2)
    permission_classes = [AllowAny]  # ← DRF permission (10.4)

    def post(self, request):         # ← обработка POST
        serializer = LoginSerializer(data=request.data)  # ← Сериализатор (10.2)
        serializer.is_valid(raise_exception=True)        # ← валидация

        user = CustomUser.objects.get(email=...)         # ← ORM (9.4)
        if not user.check_password(password):            # ← Метод модели (4.1)
            return Response(status=401)                  # ← HTTP-ответ (7.1)

        access = generate_access_token(user)             # ← JWT (11.3)
        refresh, _ = generate_refresh_token(user)
        return Response({"access": access, "refresh": refresh})
```

### 13.4 rbac/models.py

```python
# 5 таблиц RBAC (раздел 12.1)
class Resource(models.Model):     # «К чему» применяется правило
    codename = models.SlugField(unique=True)  # "documents"

class Action(models.Model):      # «Что» можно сделать
    codename = models.SlugField(unique=True)  # "read", "create"

class Role(models.Model):        # Набор разрешений
    codename = models.SlugField(unique=True)  # "admin", "editor"

class Permission(models.Model):  # Связка: роль + ресурс + действие
    role = models.ForeignKey(Role, ...)
    resource = models.ForeignKey(Resource, ...)
    action = models.ForeignKey(Action, ...)
    class Meta:
        unique_together = [("role", "resource", "action")]  # нет дублей

class UserRole(models.Model):    # Назначение роли пользователю
    user = models.ForeignKey(CustomUser, ...)
    role = models.ForeignKey(Role, ...)
```

### 13.5 business/views.py — Mock-Views

```python
# Бизнес-объекты — без реальных таблиц в БД (задание позволяет)
MOCK_DOCUMENTS = [
    {"id": 1, "title": "Договор аренды", "status": "подписан"},
    {"id": 2, "title": "Приказ", "status": "черновик"},
]

class DocumentViewSet(viewsets.ViewSet):
    rbac_resource = "documents"                        # ← RBAC
    rbac_action_map = {"get": "read", "post": "create", ...}
    permission_classes = [IsAuthenticated, RBACPermission]  # ← 401/403

    def list(self, request):
        return Response(MOCK_DOCUMENTS)  # ← Возвращаем моковые данные
```

### 13.6 middleware.py — JWT Middleware

```python
class JWTAuthenticationMiddleware(MiddlewareMixin):
    """Выполняется ДО того, как запрос попадёт в View."""

    def process_request(self, request):
        auth = JWTAuthentication()
        try:
            result = auth.authenticate(request)
            if result:
                request.user, _ = result  # ← подмена пользователя
        except Exception:
            pass

        if request.user is None:
            request.user = AnonymousUser()  # ← не аутентифицирован
```

---

## Приложение: Шпаргалка команд

```bash
# Django
python manage.py runserver           # запустить dev-сервер
python manage.py makemigrations      # создать миграции
python manage.py migrate             # применить миграции
python manage.py seed_data           # заполнить тестовыми данными
python manage.py test                # запустить тесты
python manage.py test accounts -v 2  # тесты одного приложения
python manage.py createsuperuser     # создать суперпользователя

# Git
git init                             # инициализировать репозиторий
git add .                            # добавить все файлы
git commit -m "сообщение"            # закоммитить
git push origin main                 # отправить на GitHub
git pull                             # получить изменения

# GitHub CLI
gh repo create имя --public --push   # создать репо и запушить
gh auth status                       # проверить авторизацию
```

---

> **Следующий шаг:** после изучения каждого раздела попробуйте
> написать соответствующий файл проекта самостоятельно,
> сверяясь с оригиналом в auth-system.
