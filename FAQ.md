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


1. Serializers.py - детальный разбор

# Импортируем базовый класс для создания сериализаторов
from rest_framework import serializers

# Импортируем нашу модель Note из текущего приложения
from .models import Note

# Создаём класс сериализатора, который наследуется от ModelSerializer
class NoteSerializer(serializers.ModelSerializer):
    # Кастомизируем поле user - вместо ID показываем username
    # ReadOnlyField означает, что это поле нельзя изменить через API
    # source='user.username' говорит: "возьми объект user, затем его поле username"
    user = serializers.ReadOnlyField(source='user.username')

    # Вложенный класс Meta содержит настройки сериализатора
    class Meta:
        # Указываем, какую модель использовать для автоматического создания полей
        model = Note
        
        # Список полей, которые будут включены в JSON ответ
        # Порядок полей определяет порядок в JSON
        fields = ['id', 'title', 'content', 'created_at', 'updated_at', 'user']
        
        # Поля, которые нельзя изменять через API (только для чтения)
        # Эти поля будут проигнорированы при POST, PUT, PATCH запросах
        read_only_fields = ['created_at', 'updated_at']


2. Views.py - детальный разбор
# Импортируем готовые классы для создания API views
# generics содержит базовые классы для типичных операций (List, Create, Retrieve, Update, Delete)
# permissions содержит классы для проверки прав доступа
from rest_framework import generics, permissions

# Импортируем нашу модель Note из текущего приложения
from .models import Note

# Импортируем наш сериализатор из того же приложения
from .serializers import NoteSerializer

# Создаём класс для обработки GET (список) и POST (создание) запросов
# ListCreateAPIView автоматически создаёт два эндпоинта:
# - GET /api/notes/ - получить список заметок
# - POST /api/notes/ - создать новую заметку
class NoteListCreate(generics.ListCreateAPIView):
    # Указываем, какой сериализатор использовать для преобразования данных
    # DRF автоматически использует его для валидации и сериализации
    serializer_class = NoteSerializer
    
    # Список классов для проверки прав доступа
    # IsAuthenticated означает, что пользователь должен быть авторизован
    # Если не авторизован, DRF вернёт 401 Unauthorized
    permission_classes = [permissions.IsAuthenticated]

    # Метод, который DRF вызывает для получения списка объектов
    # self.request.user - текущий авторизованный пользователь
    def get_queryset(self):
        # Возвращаем только заметки текущего пользователя
        # Это обеспечивает безопасность - пользователь видит только свои данные
        # filter() создаёт QuerySet с условием WHERE user = текущий_пользователь
        return Note.objects.filter(user=self.request.user)

    # Метод, который DRF вызывает при создании нового объекта
    # serializer - уже валидированный сериализатор с данными
    def perform_create(self, serializer):
        # Сохраняем объект, автоматически устанавливая владельца
        # user=self.request.user передаётся в метод save() сериализатора
        # Это гарантирует, что заметка будет привязана к текущему пользователю
        serializer.save(user=self.request.user)

# Создаём класс для обработки GET, PUT, PATCH, DELETE запросов к одной заметке
# RetrieveUpdateDestroyAPIView автоматически создаёт четыре эндпоинта:
# - GET /api/notes/1/ - получить заметку с id=1
# - PUT /api/notes/1/ - полностью заменить заметку
# - PATCH /api/notes/1/ - частично обновить заметку
# - DELETE /api/notes/1/ - удалить заметку
class NoteDetailView(generics.RetrieveUpdateDestroyAPIView):
    # Указываем, какой сериализатор использовать
    serializer_class = NoteSerializer
    
    # Список классов для проверки прав доступа
    permission_classes = [permissions.IsAuthenticated]

    # Метод, который DRF вызывает для получения объекта
    # Используется для всех операций (GET, PUT, PATCH, DELETE)
    def get_queryset(self):
        # Возвращаем только заметки текущего пользователя
        # Это обеспечивает безопасность - пользователь может работать только со своими заметками
        # Если попытаться получить заметку другого пользователя, получим 404 Not Found
        return Note.objects.filter(user=self.request.user)

3. URLs.py - детальный разбор
# Импортируем функцию path для создания URL маршрутов
# path() принимает строку URL и view функцию/класс
from django.urls import path

# Импортируем наши view классы из текущего приложения
# NoteListCreate - для списка и создания заметок
# NoteDetailView - для работы с одной заметкой
from .views import NoteListCreate, NoteDetailView

# Список URL маршрутов для этого приложения
# Django будет искать совпадения в этом списке
urlpatterns = [
    # Маршрут для списка и создания заметок
    # '' - пустой путь (корень /api/notes/)
    # NoteListCreate.as_view() - преобразует класс в view функцию
    # Django автоматически вызывает as_view() для создания функции-обработчика
    # name='note-list-create' - имя для обратных ссылок (reverse URL lookup)
    path('', NoteListCreate.as_view(), name='note-list-create'),
    
    # Маршрут для работы с одной заметкой
    # '<int:pk>/' - путь с параметром (например, /api/notes/1/)
    # <int:pk> - целое число, которое будет передано в view как параметр pk
    # int: - конвертер типа (гарантирует, что pk будет целым числом)
    # pk - имя параметра (primary key - первичный ключ)
    # NoteDetailView.as_view() - преобразует класс в view функцию
    # name='note-detail' - имя для обратных ссылок
    path('<int:pk>/', NoteDetailView.as_view(), name='note-detail'),
]

4. Главный URLs.py - детальный разбор
# Импортируем админку Django
from django.contrib import admin

# Импортируем функции для работы с URL
# path - для создания маршрутов
# include - для включения URL из других приложений
from django.urls import path, include

# Список URL маршрутов для всего проекта
# Django ищет совпадения в этом списке по порядку
urlpatterns = [
    # Маршрут для админки Django
    # 'admin/' - префикс URL (админка будет доступна по /admin/)
    # admin.site.urls - встроенные URL админки Django
    # Когда пользователь переходит на /admin/, Django показывает админку
    path('admin/', admin.site.urls),
    
    # Маршрут для нашего API заметок
    # 'api/notes/' - префикс URL (API будет доступно по /api/notes/)
    # include('notes.urls') - включает все URL из приложения notes
    # Когда пользователь переходит на /api/notes/, Django ищет совпадения в notes.urls
    # Полный путь будет: /api/notes/ + пути из notes.urls
    # Например: /api/notes/ + '' = /api/notes/
    # Например: /api/notes/ + '1/' = /api/notes/1/
    path('api/notes/', include('notes.urls')),
]

5. Models.py - детальный разбор
# Импортируем базовый класс для создания моделей Django
from django.db import models

# Импортируем встроенную модель User Django
# User содержит поля: username, email, password, first_name, last_name и др.
from django.contrib.auth.models import User

# Создаём класс модели, который наследуется от models.Model
# models.Model предоставляет базовую функциональность для работы с базой данных
class Note(models.Model):
    # Поле для заголовка заметки
    # CharField - поле для короткого текста
    # max_length=255 - максимальная длина 255 символов
    # Это поле будет обязательным (null=False, blank=False по умолчанию)
    title = models.CharField(max_length=255)
    
    # Поле для содержимого заметки
    # TextField - поле для длинного текста без ограничения длины
    # Это поле будет обязательным
    content = models.TextField()
    
    # Поле для даты создания заметки
    # DateTimeField - поле для даты и времени
    # auto_now_add=True - автоматически устанавливает текущее время при создании объекта
    # Это поле нельзя изменить после создания
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Поле для даты последнего обновления заметки
    # DateTimeField - поле для даты и времени
    # auto_now=True - автоматически обновляет время при каждом сохранении объекта
    # Это поле обновляется при каждом изменении заметки
    updated_at = models.DateTimeField(auto_now=True)
    
    # Поле для связи с пользователем (владелец заметки)
    # ForeignKey - поле для связи "один-ко-многим"
    # User - модель, с которой связываем (один пользователь может иметь много заметок)
    # on_delete=models.CASCADE - при удалении пользователя удаляются все его заметки
    # Это поле будет обязательным
    user = models.ForeignKey(User, on_delete=models.CASCADE)


6. Admin.py - детальный разбор
# Импортируем админку Django
from django.contrib import admin

# Импортируем нашу модель Note из текущего приложения
from .models import Note

# Регистрируем модель Note в админке Django
# admin.site.register() - функция для регистрации модели
# Note - модель, которую регистрируем
# После регистрации модель появится в веб-интерфейсе админки
# Администраторы смогут создавать, редактировать, удалять заметки через веб-интерфейс
admin.site.register(Note)



Последовательность выполнения запроса:
Пример: GET /api/notes/1/
Django получает запрос → ищет совпадение в главном urls.py
Находит path('api/notes/', include('notes.urls')) → переходит к notes.urls
В notes.urls находит path('<int:pk>/', NoteDetailView.as_view()) → pk=1
Создаёт экземпляр NoteDetailView → вызывает as_view()
Проверяет права → permissions.IsAuthenticated
Вызывает get_queryset() → Note.objects.filter(user=request.user)
Ищет заметку → queryset.get(pk=1)
Создаёт сериализатор → NoteSerializer(note)
Преобразует в JSON → serializer.data
Возвращает ответ → HTTP 200 с JSON