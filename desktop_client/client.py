"""
Max Messenger Desktop Client
Клиент для мессенджера Max на PyQt6
"""

import sys
import os
import asyncio
from pathlib import Path
from typing import Optional, Dict, Any, List

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QListWidget, QListWidgetItem,
    QTextEdit, QSplitter, QFileDialog, QMessageBox, QScrollArea,
    QFrame, QSizePolicy, QStackedWidget, QToolBar, QStatusBar,
    QSystemTrayIcon, QMenu, QAction, QProgressBar, QComboBox
)
from PyQt6.QtCore import (
    Qt, QThread, pyqtSignal, QObject, QTimer, QUrl, QSize
)
from PyQt6.QtGui import (
    QIcon, QFont, QPixmap, QImage, QAction, QKeySequence,
    QTextCursor, QTextDocument, QDesktopServices
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PIL import Image

# Добавляем родительскую директорию в path для импорта pymax_wrapper
sys.path.insert(0, str(Path(__file__).parent.parent))
from pymax_wrapper import MaxAPI


# ==================== Стили ====================

STYLESHEET = """
QMainWindow {
    background-color: #1e1e2e;
}

QWidget {
    background-color: #1e1e2e;
    color: #cdd6f4;
    font-family: 'Segoe UI', Arial, sans-serif;
}

QLineEdit, QTextEdit {
    background-color: #313244;
    border: 2px solid #45475a;
    border-radius: 8px;
    padding: 8px;
    color: #cdd6f4;
    font-size: 14px;
}

QLineEdit:focus, QTextEdit:focus {
    border-color: #89b4fa;
}

QPushButton {
    background-color: #89b4fa;
    color: #1e1e2e;
    border: none;
    border-radius: 8px;
    padding: 10px 20px;
    font-weight: bold;
    font-size: 14px;
}

QPushButton:hover {
    background-color: #b4befe;
}

QPushButton:pressed {
    background-color: #7287fd;
}

QPushButton:disabled {
    background-color: #45475a;
    color: #6c7086;
}

QListWidget {
    background-color: #313244;
    border: none;
    border-radius: 8px;
    outline: none;
}

QListWidget::item {
    padding: 12px;
    border-bottom: 1px solid #45475a;
}

QListWidget::item:selected {
    background-color: #45475a;
}

QListWidget::item:hover {
    background-color: #3a3b4f;
}

QScrollArea {
    border: none;
    background-color: #1e1e2e;
}

QToolBar {
    background-color: #313244;
    border: none;
    padding: 5px;
    spacing: 5px;
}

QStatusBar {
    background-color: #313244;
    color: #a6adc8;
}

QLabel {
    color: #cdd6f4;
}

QLabel#title {
    font-size: 24px;
    font-weight: bold;
    color: #89b4fa;
}

QLabel#subtitle {
    font-size: 14px;
    color: #a6adc8;
}

QComboBox {
    background-color: #313244;
    border: 2px solid #45475a;
    border-radius: 8px;
    padding: 8px;
    color: #cdd6f4;
}

QComboBox::drop-down {
    border: none;
    width: 30px;
}

QComboBox QAbstractItemView {
    background-color: #313244;
    border: 2px solid #45475a;
    selection-background-color: #45475a;
}
"""

# ==================== Worker для асинхронных операций ====================

class AsyncWorker(QObject):
    """Worker для выполнения асинхронных операций в отдельном потоке"""
    finished = pyqtSignal(object)
    error = pyqtSignal(str)
    progress = pyqtSignal(int)

    def __init__(self, coro):
        super().__init__()
        self.coro = coro

    def run(self):
        try:
            result = asyncio.run(self.coro)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


# ==================== Окно авторизации ====================

class LoginWindow(QMainWindow):
    """Окно авторизации"""

    def __init__(self, callback):
        super().__init__()
        self.callback = callback
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Max Messenger - Авторизация")
        self.setMinimumSize(400, 300)
        self.setMaximumSize(400, 300)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)

        # Заголовок
        title = QLabel("🔐 Max Messenger")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        subtitle = QLabel("Войдите в свой аккаунт")
        subtitle.setObjectName("subtitle")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)

        layout.addSpacing(20)

        # Ввод номера
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("+79991234567")
        self.phone_input.returnPressed.connect(self.login)
        layout.addWidget(self.phone_input)

        # Кнопка входа
        self.login_btn = QPushButton("Войти")
        self.login_btn.clicked.connect(self.login)
        layout.addWidget(self.login_btn)

        # Статус
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: #f38ba8;")
        layout.addWidget(self.status_label)

    def login(self):
        phone = self.phone_input.text().strip()
        if not phone:
            self.status_label.setText("❌ Введите номер телефона")
            return

        if not phone.startswith("+"):
            phone = "+" + phone

        self.status_label.setText("⏳ Подключение...")
        self.login_btn.setEnabled(False)

        # Запускаем авторизацию в отдельном потоке
        self.worker_thread = QThread()
        self.worker = AsyncWorker(self.callback(phone))
        self.worker.moveToThread(self.worker_thread)

        self.worker_thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.on_login_success)
        self.worker.error.connect(self.on_login_error)
        self.worker.finished.connect(self.worker_thread.quit)
        self.worker.error.connect(self.worker_thread.quit)
        self.worker_thread.finished.connect(self.worker_thread.deleteLater)

        self.worker_thread.start()

    async def callback(self, phone: str):
        """Вызывается из основного потока для авторизации"""
        return await self.callback_coro(phone)

    async def callback_coro(self, phone: str):
        """Корутина авторизации"""
        # Создаём клиента и подключаемся
        api = MaxAPI(phone)
        
        # Запускаем подключение с таймаутом
        connect_task = asyncio.create_task(api.connect())
        try:
            await asyncio.wait_for(connect_task, timeout=60)
        except asyncio.TimeoutError:
            raise TimeoutError("Превышено время ожидания QR-кода")
        
        return api

    def on_login_success(self, api):
        self.hide()
        self.main_window = MainWindow(api)
        self.main_window.show()

    def on_login_error(self, error):
        self.status_label.setText(f"❌ {error}")
        self.login_btn.setEnabled(True)


# ==================== Основное окно ====================

class MainWindow(QMainWindow):
    """Главное окно приложения"""

    def __init__(self, api: MaxAPI):
        super().__init__()
        self.api = api
        self.current_chat_id: Optional[str] = None
        self.chats_data: List[Dict] = []
        self.messages_data: List[Dict] = []
        self.init_ui()
        self.load_chats()

    def init_ui(self):
        self.setWindowTitle("Max Messenger")
        self.setMinimumSize(900, 600)

        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Левая панель - список чатов
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(0)
        left_layout.setContentsMargins(0, 0, 0, 0)

        # Заголовок
        header = QWidget()
        header.setStyleSheet("background-color: #313244; padding: 15px;")
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(15, 15, 15, 15)

        self.profile_label = QLabel("Загрузка...")
        self.profile_label.setStyleSheet("font-weight: bold; font-size: 16px; color: #89b4fa;")
        header_layout.addWidget(self.profile_label)

        self.status_label = QLabel("online")
        self.status_label.setStyleSheet("color: #a6e3a1; font-size: 12px;")
        header_layout.addWidget(self.status_label)

        left_layout.addWidget(header)

        # Поиск
        search_layout = QHBoxLayout()
        search_layout.setContentsMargins(10, 10, 10, 10)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Поиск чатов...")
        self.search_input.textChanged.connect(self.filter_chats)
        search_layout.addWidget(self.search_input)
        left_layout.addLayout(search_layout)

        # Список чатов
        self.chat_list = QListWidget()
        self.chat_list.itemClicked.connect(self.on_chat_selected)
        left_layout.addWidget(self.chat_list)

        splitter.addWidget(left_panel)

        # Правая панель - чат
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setSpacing(0)
        right_layout.setContentsMargins(0, 0, 0, 0)

        # Заголовок чата
        chat_header = QWidget()
        chat_header.setStyleSheet("background-color: #313244; padding: 15px;")
        chat_header_layout = QHBoxLayout(chat_header)
        chat_header_layout.setContentsMargins(15, 15, 15, 15)

        self.chat_title_label = QLabel("Выберите чат")
        self.chat_title_label.setStyleSheet("font-weight: bold; font-size: 18px;")
        chat_header_layout.addWidget(self.chat_title_label)

        chat_header_layout.addStretch()

        right_layout.addWidget(chat_header)

        # Область сообщений
        self.messages_area = QScrollArea()
        self.messages_area.setWidgetResizable(True)
        self.messages_content = QWidget()
        self.messages_layout = QVBoxLayout(self.messages_content)
        self.messages_layout.setSpacing(10)
        self.messages_layout.setContentsMargins(15, 15, 15, 15)
        self.messages_layout.addStretch()
        self.messages_area.setWidget(self.messages_content)
        right_layout.addWidget(self.messages_area)

        # Ввод сообщения
        input_layout = QHBoxLayout()
        input_layout.setContentsMargins(15, 15, 15, 15)
        input_layout.setSpacing(10)

        # Кнопки прикрепления
        attach_btn = QPushButton("📎")
        attach_btn.setFixedSize(40, 40)
        attach_btn.clicked.connect(self.attach_file)
        input_layout.addWidget(attach_btn)

        self.message_input = QTextEdit()
        self.message_input.setPlaceholderText("Напишите сообщение...")
        self.message_input.setMaximumHeight(100)
        self.message_input.setMinimumHeight(50)
        self.message_input.installEventFilter(self)
        input_layout.addWidget(self.message_input, 1)

        send_btn = QPushButton("➤")
        send_btn.setFixedSize(50, 50)
        send_btn.clicked.connect(self.send_message)
        input_layout.addWidget(send_btn)

        right_layout.addLayout(input_layout)

        splitter.addWidget(right_panel)
        splitter.setSizes([250, 650])

        main_layout.addWidget(splitter)

        # Status bar
        self.statusBar().showMessage("Готов к работе")

        # Загружаем профиль
        self.load_profile()

    def eventFilter(self, obj, event):
        """Перехват событий для отправки по Enter"""
        from PyQt6.QtCore import QEvent
        from PyQt6.QtGui import QKeyEvent
        
        if obj == self.message_input and event.type() == QEvent.Type.KeyPress:
            key_event = event
            if key_event.key() == Qt.Key.Key_Return and not key_event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                self.send_message()
                return True
        return super().eventFilter(obj, event)

    async def load_profile_coro(self):
        """Загрузка профиля"""
        profile = await self.api.get_profile()
        return profile

    def load_profile(self):
        """Загрузка профиля пользователя"""
        async def _load():
            profile = await self.api.get_profile()
            self.profile_label.setText(f"👤 {profile.get('name', 'User')}")
            return profile
        
        from functools import partial
        asyncio.ensure_future(_load())

    async def load_chats_coro(self):
        """Загрузка списка чатов"""
        dialogs = await self.api.get_dialogs()
        return dialogs

    def load_chats(self):
        """Загрузка чатов"""
        async def _load():
            try:
                dialogs = await self.api.get_dialogs()
                self.chats_data = dialogs
                self.update_chat_list()
                self.statusBar().showMessage(f"Загружено {len(dialogs)} чатов")
            except Exception as e:
                self.statusBar().showMessage(f"Ошибка: {e}")
        
        asyncio.ensure_future(_load())

    def update_chat_list(self):
        """Обновление списка чатов"""
        self.chat_list.clear()
        for chat in self.chats_data:
            item = QListWidgetItem(f"{chat.get('name', 'Unknown')}")
            item.setData(Qt.ItemDataRole.UserRole, chat.get('id'))
            unread = chat.get('unread_count', 0)
            if unread > 0:
                item.setBackground(Qt.GlobalColor.darkYellow)
            self.chat_list.addItem(item)

    def filter_chats(self, text):
        """Фильтрация чатов по поиску"""
        for i in range(self.chat_list.count()):
            item = self.chat_list.item(i)
            item.setHidden(text.lower() not in item.text().lower())

    def on_chat_selected(self, item):
        """Выбор чата"""
        chat_id = item.data(Qt.ItemDataRole.UserRole)
        self.current_chat_id = chat_id
        
        # Находим название чата
        for chat in self.chats_data:
            if chat.get('id') == chat_id:
                self.chat_title_label.setText(chat.get('name', 'Chat'))
                break
        
        self.load_messages(chat_id)

    async def load_messages_coro(self, chat_id: str):
        """Загрузка сообщений"""
        history = await self.api.get_chat_history(chat_id, limit=50)
        return history

    def load_messages(self, chat_id: str):
        """Загрузка сообщений чата"""
        # Очистка
        while self.messages_layout.count() > 1:
            item = self.messages_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        async def _load():
            try:
                messages = await self.api.get_chat_history(chat_id, limit=50)
                self.messages_data = messages
                
                # Добавляем сообщения в обратном порядке (новые внизу)
                for msg in reversed(messages):
                    self.add_message_to_ui(msg)
                
                # Прокрутка вниз
                self.messages_area.verticalScrollBar().setValue(
                    self.messages_area.verticalScrollBar().maximum()
                )
            except Exception as e:
                self.statusBar().showMessage(f"Ошибка загрузки: {e}")
        
        asyncio.ensure_future(_load())

    def add_message_to_ui(self, msg: Dict):
        """Добавление сообщения в UI"""
        msg_widget = QWidget()
        msg_widget.setStyleSheet("""
            QWidget {
                background-color: #45475a;
                border-radius: 10px;
                padding: 10px;
                margin: 5px 0;
            }
        """)
        
        layout = QVBoxLayout(msg_widget)
        
        # Текст сообщения
        text = msg.get('text', '')
        if text:
            text_label = QLabel(text)
            text_label.setWordWrap(True)
            text_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            layout.addWidget(text_label)
        
        # Если есть вложение (фото/видео)
        media_type = msg.get('media_type')
        media_url = msg.get('media_url')
        
        if media_type and media_url:
            if media_type.startswith('image'):
                # Фото - показываем превью
                img_label = QLabel()
                img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                pixmap = QPixmap(media_url)
                if not pixmap.isNull():
                    img_label.setPixmap(pixmap.scaled(300, 300, Qt.AspectRatioMode.KeepAspectRatio))
                    img_label.mouseDoubleClickEvent = lambda e: self.open_media(media_url, 'image')
                    img_label.setCursor(Qt.CursorShape.PointingHandCursor)
                    layout.addWidget(img_label)
            elif media_type.startswith('video'):
                # Видео - показываем плеер
                player = self.create_video_player(media_url)
                layout.addWidget(player)
        
        # Дата
        date_label = QLabel(f"{msg.get('sender_id')} • {msg.get('date', '')}")
        date_label.setStyleSheet("color: #a6adc8; font-size: 11px;")
        date_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(date_label)
        
        self.messages_layout.insertWidget(self.messages_layout.count() - 1, msg_widget)

    def create_video_player(self, url: str) -> QWebEngineView:
        """Создание видео плеера"""
        player = QWebEngineView()
        player.setMaximumHeight(300)
        player.setMinimumSize(400, 250)
        
        # HTML для видео плеера
        html = f"""
        <html>
        <body style="margin:0; background:#000; display:flex; justify-content:center; align-items:center; height:100vh;">
            <video controls autoplay style="max-width:100%; max-height:100%;">
                <source src="{url}">
                Your browser does not support the video tag.
            </video>
        </body>
        </html>
        """
        player.setHtml(html)
        return player

    def open_media(self, url: str, media_type: str):
        """Открытие медиа в полном размере"""
        if media_type == 'image':
            # Открываем в браузере
            QDesktopServices.openUrl(QUrl.fromLocalFile(url))

    def send_message(self):
        """Отправка сообщения"""
        if not self.current_chat_id:
            QMessageBox.warning(self, "Ошибка", "Выберите чат")
            return
        
        text = self.message_input.toPlainText().strip()
        if not text:
            return
        
        self.message_input.clear()
        
        async def _send():
            try:
                success = await self.api.send_message(self.current_chat_id, text)
                if success:
                    self.statusBar().showMessage("Сообщение отправлено")
                    # Добавляем сообщение в UI
                    self.add_message_to_ui({
                        'text': text,
                        'sender_id': 'Вы',
                        'date': 'только что'
                    })
                else:
                    self.statusBar().showMessage("Ошибка отправки")
            except Exception as e:
                self.statusBar().showMessage(f"Ошибка: {e}")
        
        asyncio.ensure_future(_send())

    def attach_file(self):
        """Прикрепление файла"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите файл",
            "",
            "Все файлы (*);;Изображения (*.png *.jpg *.jpeg *.gif);;Видео (*.mp4 *.avi *.mkv);;Документы (*.pdf *.doc *.docx *.txt)"
        )
        
        if file_path:
            self.send_file(file_path)

    def send_file(self, file_path: str):
        """Отправка файла"""
        if not self.current_chat_id:
            QMessageBox.warning(self, "Ошибка", "Выберите чат")
            return
        
        async def _send():
            try:
                # Определяем тип файла
                ext = Path(file_path).suffix.lower()
                media_type = 'document'
                
                if ext in ['.png', '.jpg', '.jpeg', '.gif', '.webp']:
                    media_type = 'image'
                elif ext in ['.mp4', '.avi', '.mkv', '.webm']:
                    media_type = 'video'
                elif ext in ['.mp3', '.wav', '.ogg', '.flac']:
                    media_type = 'audio'
                
                # Отправляем как документ
                # Примечание: метод может отличаться в зависимости от версии PyMax
                success = await self.api.client.send_file(
                    chat_id=self.current_chat_id,
                    file=file_path,
                    caption=f"Файл: {Path(file_path).name}"
                )
                
                if success:
                    self.statusBar().showMessage(f"Файл отправлен: {Path(file_path).name}")
                else:
                    self.statusBar().showMessage("Ошибка отправки файла")
            except Exception as e:
                self.statusBar().showMessage(f"Ошибка: {e}")
        
        asyncio.ensure_future(_send())

    def closeEvent(self, event):
        """Закрытие приложения"""
        asyncio.ensure_future(self.api.disconnect())
        event.accept()


# ==================== Запуск приложения ====================

def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLESHEET)
    
    # Иконка приложения
    # app.setWindowIcon(QIcon('icon.png'))
    
    # Показываем окно авторизации
    async def on_login(phone: str):
        api = MaxAPI(phone)
        await api.connect()
        return api
    
    login_window = LoginWindow(on_login)
    login_window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
