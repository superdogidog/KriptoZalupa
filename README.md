# KriptoZalupa — Max Messenger Client

Десктопный клиент и инструменты для мессенджера Max.

---

## 📋 Оглавление

1. [Desktop клиент](#desktop-клиент)
2. [PyMax Wrapper](#pymax-wrapper)
3. [Документация](#документация)

---

## 🖥️ Desktop клиент

Полноценное GUI-приложение на PyQt6 с поддержкой:
- 🔐 Авторизация по QR-коду
- 💬 Список чатов с поиском
- ✉️ Отправка сообщений и медиа
- 🖼️ Просмотр фото и видео внутри чата
- 📎 Прикрепление файлов

**Запуск:**
```bash
cd desktop_client
pip install -r requirements.txt
python client.py
```

**Документация:** [desktop_client/README.md](desktop_client/README.md)

---

## 🧩 PyMax Wrapper

Модуль `pymax_wrapper.py` предоставляет удобный интерфейс для работы с Max API.

**Основные функции:**
- `get_contacts()` — список контактов
- `get_chats()`, `get_dialogs()` — список чатов
- `send_message()` — отправка сообщений
- `get_profile()`, `update_profile()` — управление профилем
- `get_channels()`, `create_channel()` — управление каналами

**Документация:** [API.md](API.md)

---

## 📁 Структура проекта

```
KriptoZalupa/
├── desktop_client/       # PyQt6 приложение
│   ├── client.py
│   ├── requirements.txt
│   └── README.md
├── pymax_wrapper.py      # Wrapper для API
├── API.md               # Документация API
├── main.py              # Пример авторизации
└── README.md            # Главная документация
```

---

## 🔗 Ссылки

- [PyMax GitHub](https://github.com/MaxApiTeam/PyMax)
- [Max API Documentation](https://docs.maxapi.io/)
