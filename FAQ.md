# FAQ - Notes API Project

## Последовательность создания проекта

### 1. Настройка проекта

#### Создание виртуального окружения
```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
# или
venv\Scripts\activate  # Windows
```

#### Установка зависимостей
```bash
pip install django djangorestframework psycopg2-binary python-decouple
pip freeze > requirements.txt
```

#### Создание Django проекта
```bash
django-admin startproject notes_api .
```

#### Создание приложений
```bash
python manage.py startapp users
python manage.py startapp notes
```

### 2. Настройка Docker и PostgreSQL

#### Создание docker-compose.yml
```yaml
version: '3.8'

services:
  db:
    image: postgres:13
    environment:
      POSTGRES_DB: notes_db
      POSTGRES_USER: notes_user
      POSTGRES_PASSWORD: notes_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

**Объяснение:**
- `ports: "5432:5432"` - маппинг портов (локальный:контейнер)
- `volumes` - сохранение данных между перезапусками
- `environment` - переменные окружения для PostgreSQL

#### Запуск PostgreSQL
```bash
docker-compose up -d
```

### 3. Настройка Django

#### Обновление settings.py
```python
# notes_api/settings.py

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',  # DRF
    'users',          # наше приложение
    'notes',          # наше приложение
]

# Настройки базы данных
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'notes_db',
        'USER': 'notes_user',
        'PASSWORD': 'notes_password',
        'HOST': 'localhost',  # Docker Compose делает доступным на localhost
        'PORT': '5432',
    }
}
```

### 4. Создание моделей

#### Модель Note (notes/models.py)
```python
from django.db import models
from django.contrib.auth.models import User

class Note(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']
```

**Объяснение полей:**
- `auto_now_add=True` - устанавливается только при создании
- `auto_now=True` - обновляется при каждом сохранении
- `on_delete=models.CASCADE` - при удалении пользователя удаляются его заметки

### 5. Миграции

#### Создание миграций
```bash
python manage.py makemigrations
```

#### Применение миграций
```bash
python manage.py migrate
```

**Зачем нужны миграции:**
- Django создает SQL-скрипты для изменения структуры БД
- Даже встроенные приложения (admin, auth) требуют миграций
- Миграции можно откатывать и применять пошагово

### 6. Создание суперпользователя

```bash
python manage.py createsuperuser
```

**Назначение суперпользователя:**
- Доступ к Django Admin
- Управление данными через веб-интерфейс
- Создание других пользователей

### 7. Настройка Django Admin

#### Регистрация модели (notes/admin.py)
```python
from django.contrib import admin
from .models import Note

@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'created_at', 'updated_at')
    list_filter = ('created_at', 'user')
    search_fields = ('title', 'content')
```

### 8. Создание REST API

#### Сериализатор (notes/serializers.py)
```python
from rest_framework import serializers
from .models import Note

class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = ['id', 'title', 'content', 'created_at', 'updated_at', 'user']
        read_only_fields = ['created_at', 'updated_at', 'user']
```

**Объяснение:**
- `ModelSerializer` автоматически создает поля на основе модели
- `read_only_fields` - поля, которые нельзя изменять через API
- `user` будет устанавливаться автоматически при создании

#### Представления (notes/views.py)
```python
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Note
from .serializers import NoteSerializer

class NoteListCreate(generics.ListCreateAPIView):
    serializer_class = NoteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Note.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class NoteDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = NoteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Note.objects.filter(user=self.request.user)
```

**Объяснение:**
- `ListCreateAPIView` - GET (список) + POST (создание)
- `RetrieveUpdateDestroyAPIView` - GET (детали) + PUT/PATCH + DELETE
- `get_queryset()` - фильтрация по текущему пользователю
- `perform_create()` - автоматическое назначение пользователя

#### URL-маршруты (notes/urls.py)
```python
from django.urls import path
from .views import NoteListCreate, NoteDetailView

urlpatterns = [
    path('notes/', NoteListCreate.as_view(), name='note-list-create'),
    path('notes/<int:pk>/', NoteDetailView.as_view(), name='note-detail'),
]
```

#### Подключение URL (notes_api/urls.py)
```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('notes.urls')),
]
```

### 9. Тестирование API

#### Создание заметки
```bash
curl -X POST http://localhost:8000/api/notes/ \
  -H "Content-Type: application/json" \
  -d '{"title": "Моя первая заметка", "content": "Содержание заметки"}'
```

#### Получение списка заметок
```bash
curl http://localhost:8000/api/notes/
```

#### Обновление заметки
```bash
curl -X PATCH http://localhost:8000/api/notes/1/ \
  -H "Content-Type: application/json" \
  -d '{"title": "Обновленный заголовок"}'
```

#### Удаление заметки
```bash
curl -X DELETE http://localhost:8000/api/notes/1/
```

### 10. HTTP методы

- **GET** - получение данных
- **POST** - создание нового ресурса
- **PUT** - полное обновление ресурса
- **PATCH** - частичное обновление ресурса
- **DELETE** - удаление ресурса

**Разница PUT vs PATCH:**
- PUT требует все поля
- PATCH позволяет обновить только указанные поля

### 11. Коды ответов

- **200** - успешный запрос
- **201** - ресурс создан
- **400** - ошибка в запросе
- **401** - не авторизован
- **403** - нет прав доступа
- **404** - ресурс не найден

### 12. Следующие шаги

1. **JWT аутентификация**
   - Установка `djangorestframework-simplejwt`
   - Настройка токенов
   - Создание эндпоинтов для входа/регистрации

2. **Тестирование**
   - Настройка pytest
   - Написание unit-тестов
   - Тестирование API

3. **Дополнительные функции**
   - Поиск по заметкам
   - Пагинация
   - Фильтрация

### 13. Полезные команды

```bash
# Запуск сервера разработки
python manage.py runserver

# Создание миграций
python manage.py makemigrations

# Применение миграций
python manage.py migrate

# Создание суперпользователя
python manage.py createsuperuser

# Запуск shell
python manage.py shell

# Проверка проекта
python manage.py check
```

### 14. Структура проекта

```
notes_project/
├── manage.py
├── requirements.txt
├── docker-compose.yml
├── notes_api/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── users/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── tests.py
│   └── views.py
└── notes/
    ├── __init__.py
    ├── admin.py
    ├── apps.py
    ├── models.py
    ├── serializers.py
    ├── tests.py
    ├── urls.py
    └── views.py
```

### 15. Частые проблемы

#### Ошибка импорта User
```python
# Правильно:
from django.contrib.auth.models import User

# Неправильно:
from users.models import User
```

#### Ошибка подключения к БД
- Проверьте, что PostgreSQL запущен: `docker-compose ps`
- Проверьте настройки в `settings.py`
- Убедитесь, что миграции применены

#### Ошибки линтера в IDE
- Настройте Python interpreter в VS Code
- Игнорируйте ложные срабатывания для Django кода
- Используйте `.vscode/settings.json` для настройки

### 16. Git команды

```bash
# Инициализация репозитория
git init

# Добавление файлов
git add .

# Создание коммита
git commit -m "Initial commit"

# Проверка статуса
git status

# Просмотр истории
git log

# Отмена изменений
git reset --hard HEAD
```

### 17. Docker команды

```bash
# Запуск сервисов
docker-compose up -d

# Остановка сервисов
docker-compose down

# Просмотр логов
docker-compose logs

# Пересборка образов
docker-compose build
```

Этот FAQ содержит всю необходимую информацию для создания и понимания проекта Notes API. Используйте его как справочник при разработке! 