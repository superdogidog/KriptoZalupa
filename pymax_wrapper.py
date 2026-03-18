"""
Wrapper-модуль для PyMax библиотеки.
Предоставляет удобный интерфейс для основных операций.
Если библиотека перестанет работать, эти функции можно переписать самостоятельно.
"""

import asyncio
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any
import qrcode
from pymax import MaxClient
from pymax.payloads import UserAgentPayload


logger = logging.getLogger(__name__)


class MaxAPI:
    """
    Обёртка над PyMax для удобной работы с API Max.
    Все методы асинхронные.
    """

    def __init__(self, phone: str, work_dir: str = "cache"):
        """
        Инициализация клиента.

        :param phone: Номер телефона (например, +79991234567)
        :param work_dir: Директория для хранения сессии
        """
        self.phone = phone
        self.work_dir = work_dir
        self.client: Optional[MaxClient] = None
        self._is_authenticated = False

    async def connect(self) -> None:
        """
        Подключение к Max и авторизация через QR.
        Если сессия сохранена, используется токен.
        """
        cache_path = Path(self.work_dir)
        cache_path.mkdir(exist_ok=True)

        ua = UserAgentPayload(device_type="WEB", app_version="25.12.13")

        self.client = MaxClient(
            phone=self.phone,
            work_dir=str(cache_path),
            headers=ua,
            reconnect=True,
            reconnect_delay=2.0,
        )

        # Переопределяем метод для сохранения QR
        self.client._print_qr = lambda link: self._save_qr(link)

        await self.client.start()

    def _save_qr(self, qr_link: str) -> None:
        """Сохранение QR-кода как изображения."""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.ERROR_CORRECT_L,
            box_size=10,
            border=2,
        )
        qr.add_data(qr_link)
        qr.make(fit=True)

        qr_image = qr.make_image(fill_color="black", back_color="white")
        qr_path = Path(self.work_dir) / "qr_code.png"
        qr_image.save(qr_path)
        print(f"\n📱 QR-код: {qr_path.absolute()}")
        qr.print_ascii()

    async def disconnect(self) -> None:
        """Отключение от Max."""
        if self.client:
            await self.client.close()

    # ==================== Контакты ====================

    async def get_contacts(self) -> List[Dict[str, Any]]:
        """
        Получить список всех контактов.

        :return: Список контактов с полями id, name, phone
        """
        if not self.client:
            raise RuntimeError("Client not connected")
        return [
            {
                "id": contact.id,
                "name": str(contact.names[0]) if contact.names else "Unknown",
                "phone": contact.phone or "",
            }
            for contact in self.client.contacts
        ]

    async def add_contact(self, phone: str, first_name: str, last_name: str = "") -> bool:
        """
        Добавить новый контакт.

        :param phone: Номер телефона контакта
        :param first_name: Имя
        :param last_name: Фамилия (опционально)
        :return: True если успешно
        """
        if not self.client:
            raise RuntimeError("Client not connected")
        # Примечание: метод может отличаться в зависимости от версии PyMax
        try:
            await self.client.add_contact(phone=phone, first_name=first_name, last_name=last_name)
            return True
        except Exception as e:
            logger.error(f"Failed to add contact: {e}")
            return False

    async def remove_contact(self, contact_id: int) -> bool:
        """
        Удалить контакт по ID.

        :param contact_id: ID контакта
        :return: True если успешно
        """
        if not self.client:
            raise RuntimeError("Client not connected")
        try:
            await self.client.remove_contact(contact_id)
            return True
        except Exception as e:
            logger.error(f"Failed to remove contact: {e}")
            return False

    # ==================== Чаты ====================

    async def get_chats(self) -> List[Dict[str, Any]]:
        """
        Получить список всех чатов.

        :return: Список чатов с полями id, name, type, last_message
        """
        if not self.client:
            raise RuntimeError("Client not connected")
        return [
            {
                "id": chat.id,
                "name": chat.name if hasattr(chat, 'name') else "Unknown",
                "type": chat.type if hasattr(chat, 'type') else "private",
                "last_message": chat.last_message.text if hasattr(chat, 'last_message') and chat.last_message else None,
            }
            for chat in self.client.chats
        ]

    async def get_dialogs(self) -> List[Dict[str, Any]]:
        """
        Получить список всех диалогов.

        :return: Список диалогов с полями id, name, unread_count
        """
        if not self.client:
            raise RuntimeError("Client not connected")
        return [
            {
                "id": dialog.id,
                "name": str(dialog.peer.names[0]) if dialog.peer and dialog.peer.names else "Unknown",
                "unread_count": dialog.unread_count if hasattr(dialog, 'unread_count') else 0,
            }
            for dialog in self.client.dialogs
        ]

    async def get_chat_history(self, chat_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Получить историю сообщений чата.

        :param chat_id: ID чата
        :param limit: Количество сообщений
        :return: Список сообщений
        """
        if not self.client:
            raise RuntimeError("Client not connected")
        # Примечание: метод может отличаться в зависимости от версии PyMax
        try:
            messages = await self.client.get_history(chat_id=chat_id, limit=limit)
            return [
                {
                    "id": msg.id,
                    "text": msg.text,
                    "sender_id": msg.sender_id,
                    "date": msg.date,
                }
                for msg in messages
            ]
        except Exception as e:
            logger.error(f"Failed to get chat history: {e}")
            return []

    # ==================== Сообщения ====================

    async def send_message(self, chat_id: str, text: str) -> bool:
        """
        Отправить текстовое сообщение.

        :param chat_id: ID чата или пользователя
        :param text: Текст сообщения
        :return: True если успешно
        """
        if not self.client:
            raise RuntimeError("Client not connected")
        try:
            await self.client.send_message(chat_id=chat_id, text=text)
            return True
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            return False

    async def edit_message(self, chat_id: str, message_id: int, new_text: str) -> bool:
        """
        Редактировать сообщение.

        :param chat_id: ID чата
        :param message_id: ID сообщения
        :param new_text: Новый текст
        :return: True если успешно
        """
        if not self.client:
            raise RuntimeError("Client not connected")
        try:
            await self.client.edit_message(chat_id=chat_id, message_id=message_id, text=new_text)
            return True
        except Exception as e:
            logger.error(f"Failed to edit message: {e}")
            return False

    async def delete_message(self, chat_id: str, message_id: int) -> bool:
        """
        Удалить сообщение.

        :param chat_id: ID чата
        :param message_id: ID сообщения
        :return: True если успешно
        """
        if not self.client:
            raise RuntimeError("Client not connected")
        try:
            await self.client.delete_message(chat_id=chat_id, message_id=message_id)
            return True
        except Exception as e:
            logger.error(f"Failed to delete message: {e}")
            return False

    async def add_reaction(self, chat_id: str, message_id: int, reaction: str) -> bool:
        """
        Добавить реакцию к сообщению.

        :param chat_id: ID чата
        :param message_id: ID сообщения
        :param reaction: Эмодзи реакции
        :return: True если успешно
        """
        if not self.client:
            raise RuntimeError("Client not connected")
        try:
            await self.client.add_reaction(chat_id=chat_id, message_id=message_id, reaction=reaction)
            return True
        except Exception as e:
            logger.error(f"Failed to add reaction: {e}")
            return False

    # ==================== Профиль ====================

    async def get_profile(self) -> Dict[str, Any]:
        """
        Получить данные своего профиля.

        :return: Словарь с полями id, name, username, phone
        """
        if not self.client:
            raise RuntimeError("Client not connected")
        me = self.client.me
        return {
            "id": me.id,
            "name": str(me.names[0]) if me.names else "Unknown",
            "username": me.username if hasattr(me, 'username') else None,
            "phone": me.phone if hasattr(me, 'phone') else None,
        }

    async def get_user_profile(self, user_id: int) -> Dict[str, Any]:
        """
        Получить данные профиля пользователя по ID.

        :param user_id: ID пользователя
        :return: Словарь с полями id, name, username, phone
        """
        if not self.client:
            raise RuntimeError("Client not connected")
        # Примечание: метод может отличаться в зависимости от версии PyMax
        try:
            user = await self.client.get_user(user_id)
            return {
                "id": user.id,
                "name": str(user.names[0]) if user.names else "Unknown",
                "username": user.username if hasattr(user, 'username') else None,
                "phone": user.phone if hasattr(user, 'phone') else None,
            }
        except Exception as e:
            logger.error(f"Failed to get user profile: {e}")
            return {}

    async def update_profile(self, first_name: str = None, last_name: str = None, username: str = None) -> bool:
        """
        Обновить данные своего профиля.

        :param first_name: Новое имя
        :param last_name: Новая фамилия
        :param username: Новый username
        :return: True если успешно
        """
        if not self.client:
            raise RuntimeError("Client not connected")
        try:
            await self.client.update_profile(
                first_name=first_name,
                last_name=last_name,
                username=username,
            )
            return True
        except Exception as e:
            logger.error(f"Failed to update profile: {e}")
            return False

    async def set_avatar(self, image_path: str) -> bool:
        """
        Установить аватар профиля.

        :param image_path: Путь к изображению
        :return: True если успешно
        """
        if not self.client:
            raise RuntimeError("Client not connected")
        try:
            await self.client.set_avatar(image_path)
            return True
        except Exception as e:
            logger.error(f"Failed to set avatar: {e}")
            return False

    # ==================== Каналы/Группы ====================

    async def get_channels(self) -> List[Dict[str, Any]]:
        """
        Получить список всех каналов.

        :return: Список каналов с полями id, name, subscribers
        """
        if not self.client:
            raise RuntimeError("Client not connected")
        return [
            {
                "id": channel.id,
                "name": channel.name if hasattr(channel, 'name') else "Unknown",
                "subscribers": channel.subscribers if hasattr(channel, 'subscribers') else 0,
            }
            for channel in self.client.channels
        ]

    async def create_channel(self, name: str, description: str = "") -> Optional[int]:
        """
        Создать новый канал.

        :param name: Название канала
        :param description: Описание канала
        :return: ID созданного канала или None
        """
        if not self.client:
            raise RuntimeError("Client not connected")
        try:
            result = await self.client.create_channel(title=name, description=description)
            return result.id if result else None
        except Exception as e:
            logger.error(f"Failed to create channel: {e}")
            return None

    async def join_channel(self, channel_id: int) -> bool:
        """
        Подписаться на канал.

        :param channel_id: ID канала
        :return: True если успешно
        """
        if not self.client:
            raise RuntimeError("Client not connected")
        try:
            await self.client.join_channel(channel_id)
            return True
        except Exception as e:
            logger.error(f"Failed to join channel: {e}")
            return False

    async def leave_channel(self, channel_id: int) -> bool:
        """
        Отписаться от канала.

        :param channel_id: ID канала
        :return: True если успешно
        """
        if not self.client:
            raise RuntimeError("Client not connected")
        try:
            await self.client.leave_channel(channel_id)
            return True
        except Exception as e:
            logger.error(f"Failed to leave channel: {e}")
            return False


# ==================== Утилиты ====================

async def create_client(phone: str, work_dir: str = "cache") -> MaxAPI:
    """
    Создать и подключить клиента Max.

    :param phone: Номер телефона
    :param work_dir: Директория для сессии
    :return: Подключенный MaxAPI объект
    """
    api = MaxAPI(phone, work_dir)
    await api.connect()
    return api


def run_async(coro):
    """
    Запустить асинхронную функцию.

    :param coro: Coroutine для запуска
    :return: Результат выполнения
    """
    return asyncio.run(coro)
