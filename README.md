# PyMax Authentication — Документация

Базовая документация по аутентификации и отправке сообщений в мессенджер Max через PyMax.

---

## 📋 Оглавление

1. [Установка](#установка)
2. [Быстрый старт](#быстрый-старт)
3. [MaxAPI Wrapper](#maxapi-wrapper)
4. [Основные функции](#основные-функции)
5. [Переменные и параметры](#переменные-и-параметры)
6. [Примеры использования](#примеры-использования)

---

## 📦 Установка

```bash
pip install -U maxapi-python
```

---

## 🚀 Быстрый старт

```python
python main.py
```

1. Введите номер телефона в формате `+79991234567`
2. Отсканируйте QR-код через приложение Max
3. Готово! Сообщение отправлено в избранное

---

## 🧩 MaxAPI Wrapper

Для удобной работы с API и независимости от библиотеки создан wrapper-модуль `pymax_wrapper.py`.

**Подключение:**
```python
from pymax_wrapper import create_client, run_async

api = await create_client("+79991234567")
```

**Полная документация:** см. [API.md](API.md)

**Доступные функции:**
- 👥 `get_contacts()`, `add_contact()`, `remove_contact()`
- 💬 `get_chats()`, `get_dialogs()`, `get_chat_history()`
- ✉️ `send_message()`, `edit_message()`, `delete_message()`, `add_reaction()`
- 👤 `get_profile()`, `get_user_profile()`, `update_profile()`, `set_avatar()`
- 📢 `get_channels()`, `create_channel()`, `join_channel()`, `leave_channel()`

---

## 🔧 Основные функции

### `MaxClientWithQrSave._print_qr(qr_link: str)`
**Описание:** Генерирует и сохраняет QR-код для авторизации.
- Сохраняет QR-код как изображение в `cache/qr_code.png`
- Выводит QR-код в консоль (ASCII-графика)

**Параметры:**
- `qr_link` (str) — Ссылка/данные для QR-кода

---

### `client.send_message(chat_id: str, text: str)`
**Описание:** Отправляет текстовое сообщение в чат.

**Параметры:**
- `chat_id` (str) — ID чата или пользователя
  - `"0"` — Избранное (Saved Messages)
  - `str(client.me.id)` — Сообщение самому себе
  - `"<user_id>"` — ID другого пользователя
- `text` (str) — Текст сообщения

**Пример:**
```python
await client.send_message(
    chat_id="0",
    text="Привет, это тест!",
)
```

---

### `client.on_start` (декоратор)
**Описание:** Регистрирует функцию, которая вызывается после успешной авторизации и синхронизации.

**Пример:**
```python
@client.on_start
async def on_start():
    print(f"ID: {client.me.id}")
    await client.send_message(chat_id="0", text="Запущен!")
```

---

### `client.start()`
**Описание:** Запускает клиент — подключение к WebSocket, авторизация (QR или токен), синхронизация.

**Пример:**
```python
await client.start()
```

---

### `client.close()`
**Описание:** Закрывает соединение и освобождает ресурсы.

**Пример:**
```python
await client.close()
```

---

## 📝 Переменные и параметры

### `MaxClient` параметры

| Параметр | Тип | Описание |
|----------|-----|----------|
| `phone` | str | Номер телефона (например, `+79991234567`) |
| `work_dir` | str | Директория для хранения сессии и кэша |
| `headers` | UserAgentPayload | User-Agent для подключения |
| `reconnect` | bool | Автоматическое переподключение при ошибке |
| `reconnect_delay` | float | Задержка между переподключениями (сек) |

---

### `UserAgentPayload` параметры

| Параметр | Тип | Описание |
|----------|-----|----------|
| `device_type` | str | Тип устройства: `"WEB"`, `"DESKTOP"`, `"ANDROID"`, `"IOS"` |
| `app_version` | str | Версия приложения (например, `"25.12.13"`) |

**Важно:** Для QR-аутентификации используйте `device_type="WEB"`.

---

### `client.me` (объект пользователя)

| Атрибут | Тип | Описание |
|---------|-----|----------|
| `id` | int | User ID в Max |
| `names` | list | Список имён (first_name, last_name, username) |

**Пример доступа:**
```python
user_id = client.me.id
name = client.me.names[0] if client.me.names else "N/A"
```

---

### `chat_id` (идентификаторы чатов)

| Значение | Описание |
|----------|----------|
| `"0"` | Избранное (Saved Messages) |
| `str(client.me.id)` | Личный чат с самим собой |
| `"<user_id>"` | Чат с другим пользователем |
| `"<group_id>"` | Групповой чат |
| `"<channel_id>"` | Канал |

---

## 💡 Примеры использования

### 1. Отправка сообщения в избранное
```python
await client.send_message(
    chat_id="0",
    text="Тестовое сообщение",
)
```

### 2. Отправка сообщения пользователю
```python
await client.send_message(
    chat_id="123456789",  # ID пользователя
    text="Привет!",
)
```

### 3. Получение информации о себе
```python
@client.on_start
async def on_start():
    print(f"ID: {client.me.id}")
    print(f"Имя: {client.me.names[0]}")
```

### 4. Обработка входящих сообщений
```python
from pymax import Message
from pymax.filters import Filters

@client.on_message(Filters.chat(0))  # фильтр по ID чата
async def on_message(msg: Message):
    print(f"[{msg.sender}] {msg.text}")
    await client.send_message(
        chat_id=msg.chat_id,
        text="Ответ на сообщение",
    )
```

### 5. Добавление реакции
```python
await client.add_reaction(
    chat_id="0",
    message_id="12345",
    reaction="👍",
)
```

---

## 📁 Структура проекта

```
KriptoZalupa/
├── main.py              # Основной скрипт
├── cache/               # Кэш и сессии
│   ├── session.db       # База данных с токеном
│   └── qr_code.png      # QR-код для авторизации
└── README.md            # Эта документация
```

---

## ⚠️ Важные заметки

1. **Токен сохраняется** в `cache/session.db` — при повторном запуске QR не требуется
2. **Для QR используйте** `device_type="WEB"` в `UserAgentPayload`
3. **Время жизни QR** — ~30 секунд, после истечения будет сгенерирован новый
4. **Остановка скрипта** — `Ctrl+C`

---

## 🔗 Ссылки

- [PyMax GitHub](https://github.com/MaxApiTeam/PyMax)
- [Max API Documentation](https://docs.maxapi.io/)
