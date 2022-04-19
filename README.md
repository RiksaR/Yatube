# Yatube

## Краткое описание проекта
Yatube - социальная сеть для публикации дневников. Проект разработан по
классической MVT-архитектуре. Используется пагинация постов и кэширование.
Регистрация реализована с верификацией данных, сменой и восстановлением пароля
через почту. Написаны тесты, проверяющие работу сервиса.

Для того, чтобы запустить проект, необходимо клонировать репозиторий с помощью
команды 
```python
    git clone <адрес репозитория>
```
После этого необходимо зайти в директорию проекта и создать виртуальное
окружение с помощью команды
```python
    python -m venv venv # если у вас Windows
    python3 -m venv venv # если у вас Mac или Linux
```
Запустить виртуальное окружение
```python
    source venv/Scripts/activate # если у вас Windows
    source venv/bin/activate # если у вас Mac или Linux
```
И установить зависимости
```python
    pip install -r requirements.txt
```
После этого необходимо убедиться, что вы находитесь в директории, в которой
лежит файл manage.py, и выполнить команду
```python
    python manage.py runserver # если у вас Windows
    python3 manage.py runserver # если у вас Mac или Linux
```
В результате выполненных действий проект будет доступен в браузере по адресу
```python
http://127.0.0.1:8000/
```

### Используемые технологии
Python 3.9  
Django 3.0.5  
Pytest 5.4.1  
SQLite3  

### Автор проекта:
Смоленский Алексей
