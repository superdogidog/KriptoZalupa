import asyncio
import logging
from pathlib import Path
import qrcode
from pymax import MaxClient
from pymax.payloads import UserAgentPayload


# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger(__name__)


class MaxClientWithQrSave(MaxClient):
    """Клиент с сохранением QR-кода как изображения"""

    def _print_qr(self, qr_link: str) -> None:
        # Сохраняем QR-код как изображение
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.ERROR_CORRECT_L,
            box_size=10,
            border=2,
        )
        qr.add_data(qr_link)
        qr.make(fit=True)

        # Сохраняем в файл
        qr_image = qr.make_image(fill_color="black", back_color="white")
        qr_path = Path(self._work_dir) / "qr_code.png"
        qr_image.save(qr_path)
        print(f"\n📱 QR-код сохранён в: {qr_path.absolute()}")
        print("📱 Откройте файл и отсканируйте телефоном!")
        print("⏳ У вас есть ~30 секунд\n")

        # Выводим в консоль
        qr.print_ascii()


async def main():
    """
    Базовый пример аутентификации по QR и отправки сообщений в Max.
    
    При первом запуске будет запрошен номер телефона и QR-код.
    При повторных запусках используется сохранённая сессия.
    """
    # Ввод номера телефона
    phone = input("📞 Введите номер телефона (например, +79991234567): ").strip()
    if not phone.startswith("+"):
        phone = "+" + phone

    # Создаём директорию для кэша
    cache_dir = Path("cache")
    cache_dir.mkdir(exist_ok=True)

    # UA для WEB-клиента (требуется для QR-аутентификации)
    ua = UserAgentPayload(device_type="WEB", app_version="25.12.13")

    client = MaxClientWithQrSave(
        phone=phone,
        work_dir=str(cache_dir),
        headers=ua,
        reconnect=True,
        reconnect_delay=2.0,
    )

    # Обработчик запуска
    @client.on_start
    async def on_start():
        print(f"\n✅ Клиент запущен!")
        print(f"👤 Ваш ID: {client.me.id}")
        
        # Получаем имя (names может быть списком или объектом)
        if client.me.names:
            if isinstance(client.me.names, list):
                name = client.me.names[0] if client.me.names else "N/A"
            else:
                name = client.me.names.first_name if hasattr(client.me.names, 'first_name') else str(client.me.names)
            print(f"👤 Имя: {name}")
        else:
            print("👤 Имя: N/A")

        # Отправляем тестовое сообщение в избранное (chat_id="0")
        await client.send_message(
            chat_id="0",
            text="🔥 Тестовое сообщение из PyMax!",
        )
        print("✅ Сообщение отправлено в избранное!")

    # Запуск клиента
    print("\n🚀 Запуск клиента Max...\n")
    try:
        await client.start()
    except KeyboardInterrupt:
        print("\n👋 Остановка...")
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
