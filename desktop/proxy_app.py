import json
import threading
from tkinter import messagebox

import customtkinter as ctk
import requests
import websocket

API_URL = "http://localhost:8000/api"
WS_URL = "ws://localhost:8000/ws/status/"

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

BG_COLOR = "#ecfeff"
CARD_COLOR = "#ffffff"
PRIMARY = "#00bcd4"
TEXT = "#111827"
MUTED = "#7a7a7a"
BORDER = "#d1d5db"
BLOCK_BG = "#f0fdff"
BLOCK_BORDER = "#a5f3fc"
FONT = "Segoe UI"


class ProxyApp:
    """Desktop-приложение для подключения к прокси по ключу активации."""

    def __init__(self):
        """Инициализация окна приложения и запуск WebSocket."""
        self.root = ctk.CTk()
        self.root.title("Proxy Access Service")
        self.root.geometry("760x620")
        self.root.configure(fg_color=BG_COLOR)
        self.root.resizable(False, False)
        self.root.iconbitmap("icon.ico")

        # Объекты WebSocket-соединения
        self.ws_app = None
        self.ws_thread = None

        # Текстовые переменные для обновления интерфейса
        self.status_text = ctk.StringVar(value="Ожидание ключа")
        self.proxy_text = ctk.StringVar(value="Прокси пока не назначен")

        self.build_ui()
        self.root.protocol("WM_DELETE_WINDOW", self.close_app)

        # Запускаем WebSocket для получения статуса в реальном времени
        self.start_websocket()

        self.root.mainloop()

    def build_ui(self):
        """Создает интерфейс desktop-прилжения."""

        # Основная белая карточка
        card = ctk.CTkFrame(
            self.root,
            width=530,
            height=560,
            fg_color=CARD_COLOR,
            corner_radius=24,
            border_width=1,
            border_color=BORDER,
        )
        card.place(relx=0.5, rely=0.5, anchor="center")
        card.pack_propagate(False)

        title = ctk.CTkLabel(
            card,
            text="Proxy Access Service",
            font=(FONT, 24, "bold"),
            text_color=TEXT,
        )
        title.pack(pady=(32, 6))

        subtitle = ctk.CTkLabel(
            card,
            text="Подключение к прокси по ключу",
            font=(FONT, 15),
            text_color=MUTED,
        )
        subtitle.pack(pady=(0, 26))

        key_label = ctk.CTkLabel(
            card,
            text="Ключ активации",
            font=(FONT, 14, "bold"),
            text_color=TEXT,
        )
        key_label.pack(anchor="w", padx=45)

        # Поле ввода ключа
        self.key_entry = ctk.CTkEntry(
            card,
            width=470,
            height=54,
            corner_radius=6,
            border_width=1,
            border_color="#b0b0b0",
            fg_color="#ffffff",
            text_color=TEXT,
            placeholder_text="Вставьте ваш ключ",
            placeholder_text_color="#7a7a7a",
            font=(FONT, 15),
        )
        self.key_entry.pack(pady=(8, 22))

        connect_button = ctk.CTkButton(
            card,
            text="Подключиться",
            width=470,
            height=54,
            corner_radius=4,
            fg_color=PRIMARY,
            hover_color="#06b6d4",
            text_color="black",
            font=(FONT, 16),
            command=self.connect_proxy,
        )
        connect_button.pack(pady=(0, 22))

        # Блок статуса подключения
        status_block = ctk.CTkFrame(
            card,
            width=470,
            height=92,
            fg_color=BLOCK_BG,
            corner_radius=14,
            border_width=1,
            border_color=BLOCK_BORDER,
        )
        status_block.pack(pady=(0, 16))
        status_block.pack_propagate(False)

        status_title = ctk.CTkLabel(
            status_block,
            text="Статус подключения",
            font=(FONT, 14, "bold"),
            text_color=TEXT,
        )
        status_title.pack(anchor="w", padx=18, pady=(14, 2))

        status_value = ctk.CTkLabel(
            status_block,
            textvariable=self.status_text,
            font=(FONT, 13),
            text_color=PRIMARY,
        )
        status_value.pack(anchor="w", padx=18)

        # Блок данных назначенного прокси
        proxy_block = ctk.CTkFrame(
            card,
            width=470,
            height=118,
            fg_color=BLOCK_BG,
            corner_radius=14,
            border_width=1,
            border_color=BLOCK_BORDER,
        )
        proxy_block.pack()
        proxy_block.pack_propagate(False)

        proxy_title = ctk.CTkLabel(
            proxy_block,
            text="Данные прокси",
            font=(FONT, 14, "bold"),
            text_color=TEXT,
        )
        proxy_title.pack(anchor="w", padx=18, pady=(14, 2))

        proxy_value = ctk.CTkLabel(
            proxy_block,
            textvariable=self.proxy_text,
            font=(FONT, 13),
            text_color=PRIMARY,
            justify="left",
        )
        proxy_value.pack(anchor="w", padx=18)

    def start_websocket(self):
        """Запускает WebSocket-соединение в отдельном потоке."""
        self.ws_app = websocket.WebSocketApp(
            WS_URL,
            on_message=self.on_ws_message,
            on_error=self.on_ws_error,
            on_close=self.on_ws_close,
        )

        self.ws_thread = threading.Thread(
            target=self.ws_app.run_forever,
            daemon=True,
        )
        self.ws_thread.start()

    def on_ws_message(self, ws, message):
        """Обрабатывает входящие сообщения от WebSocket."""
        data = json.loads(message)

        status = data.get("status")
        proxy = data.get("proxy")

        # Перевод технических статусов в понятный текст
        status_map = {
            "connected": "Подключено",
            "disconnected": "Отключено",
            "no_free_vms": "Все прокси заняты.",
            "error": "Ошибка подключения",
        }

        status_text = status_map.get(
            status,
            data.get("message", "Ожидание"),
        )

        self.root.after(
            0,
            lambda: self.status_text.set(status_text),
        )

        if proxy:
            self.root.after(
                0,
                lambda: self.proxy_text.set(
                    f"Host: {proxy.get('host', '-')}\n"
                    f"Port: {proxy.get('port', '-')}\n"
                    f"Protocol: {proxy.get('protocol', '-')}"
                ),
            )

    def on_ws_error(self, ws, error):
        """Обрабатывает ошибку WebSocket-соединения."""
        self.root.after(
            0,
            lambda: self.status_text.set("Ошибка WebSocket-соединения."),
        )

    def on_ws_close(self, ws, close_status_code, close_msg):
        """Обрабатывает закрытие WebSocket-соединения."""
        self.root.after(
            0,
            lambda: self.status_text.set("Отключено"),
        )

    def connect_proxy(self):
        """Отправляет ключ активации на backend для подключения."""
        activation_key = self.key_entry.get().strip()

        if not activation_key:
            messagebox.showerror(
                "Ошибка",
                "Введите ключ активации",
            )
            return

        self.status_text.set("Подключение...")

        try:
            response = requests.post(
                f"{API_URL}/activate-key/",
                json={"activation_key": activation_key},
                timeout=10,
            )

            data = response.json()

            if response.status_code == 200:
                proxy = data.get("proxy", {})

                self.status_text.set("Подключено")

                self.proxy_text.set(
                    f"Host: {proxy.get('host', '-')}\n"
                    f"Port: {proxy.get('port', '-')}\n"
                    f"Protocol: {proxy.get('protocol', '-')}"
                )

                self.key_entry.delete(0, "end")
                return

            self.status_text.set(
                data.get("detail", "Ошибка подключения")
            )
            self.proxy_text.set("Прокси не назначен")

        except requests.exceptions.ConnectionError:
            self.status_text.set("Backend недоступен.")
            messagebox.showerror(
                "Ошибка",
                "Не удалось подключиться к Django серверу.",
            )

        except requests.exceptions.Timeout:
            self.status_text.set("Backend не ответил вовремя.")
            messagebox.showerror(
                "Ошибка",
                "Backend не ответил вовремя.",
            )

        except Exception as error:
            self.status_text.set("Ошибка запроса.")
            messagebox.showerror(
                "Ошибка",
                str(error),
            )

    def close_app(self):
        """Корректно закрывает приложение и WebSocket."""
        if self.ws_app:
            self.ws_app.close()

        self.root.destroy()


if __name__ == "__main__":
    ProxyApp()
