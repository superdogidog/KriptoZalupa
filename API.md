# MaxAPI — Документация по функциям

Краткая справка по всем доступным функциям wrapper-модуля `pymax_wrapper.py`.

---

## 📋 Подключение

| Функция | Описание |
|---------|----------|
| `create_client(phone, work_dir)` | Создать и подключить клиента Max |
| `run_async(coro)` | Запустить асинхронную функцию |
| `api.connect()` | Подключиться к Max и авторизоваться |
| `api.disconnect()` | Отключиться от Max |

---

## 👥 Контакты

| Функция | Описание |
|---------|----------|
| `get_contacts()` | Получить список всех контактов |
| `add_contact(phone, first_name, last_name)` | Добавить новый контакт |
| `remove_contact(contact_id)` | Удалить контакт по ID |

---

## 💬 Чаты и диалоги

| Функция | Описание |
|---------|----------|
| `get_chats()` | Получить список всех чатов |
| `get_dialogs()` | Получить список всех диалогов |
| `get_chat_history(chat_id, limit)` | Получить историю сообщений чата |

---

## ✉️ Сообщения

| Функция | Описание |
|---------|----------|
| `send_message(chat_id, text)` | Отправить текстовое сообщение |
| `edit_message(chat_id, message_id, new_text)` | Редактировать сообщение |
| `delete_message(chat_id, message_id)` | Удалить сообщение |
| `add_reaction(chat_id, message_id, reaction)` | Добавить реакцию к сообщению |

---

## 👤 Профиль

| Функция | Описание |
|---------|----------|
| `get_profile()` | Получить данные своего профиля |
| `get_user_profile(user_id)` | Получить профиль пользователя по ID |
| `update_profile(first_name, last_name, username)` | Обновить данные профиля |
| `set_avatar(image_path)` | Установить аватар профиля |

---

## 📢 Каналы

| Функция | Описание |
|---------|----------|
| `get_channels()` | Получить список всех каналов |
| `create_channel(name, description)` | Создать новый канал |
| `join_channel(channel_id)` | Подписаться на канал |
| `leave_channel(channel_id)` | Отписаться от канала |

---

## 📦 Возвращаемые данные

### Контакт
```python
{
    "id": 123456,      # ID контакта
    "name": "Имя",     # Имя
    "phone": "+7..."   # Телефон
}
```

### Чат / Диалог
```python
{
    "id": 123456,           # ID чата
    "name": "Название",     # Название
    "type": "private",      # Тип: private/group/channel
    "unread_count": 5       # Непрочитанные (для диалогов)
}
```

### Профиль
```python
{
    "id": 123456,       # User ID
    "name": "Имя",      # Имя
    "username": "@user",# Username
    "phone": "+7..."    # Телефон
}
```

### Сообщение
```python
{
    "id": 789,          # ID сообщения
    "text": "Привет",   # Текст
    "sender_id": 123,   # ID отправителя
    "date": 1234567890  # Timestamp
}
```

### Канал
```python
{
    "id": 123456,           # ID канала
    "name": "Название",     # Название
    "subscribers": 1000     # Количество подписчиков
}
```

---

## ⚡ Пример использования

```python
from pymax_wrapper import create_client, run_async

async def main():
    # Подключение
    api = await create_client("+79991234567")
    
    # Получить профиль
    profile = await api.get_profile()
    print(f"ID: {profile['id']}, Имя: {profile['name']}")
    
    # Получить контакты
    contacts = await api.get_contacts()
    for contact in contacts:
        print(f"{contact['name']}: {contact['phone']}")
    
    # Отправить сообщение
    await api.send_message("0", "Привет в избранное!")
    
    # Отключение
    await api.disconnect()

run_async(main())
```

---

## ⚠️ Примечания

1. Все функции **асинхронные** — используйте `await`
2. Для запуска используйте `asyncio.run()` или `run_async()`
3. Если функция возвращает `bool` — `True` означает успех
4. При ошибке функции логируют ошибку и возвращают `False`/`{}`/`[]`
