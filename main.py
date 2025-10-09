from classApp import App

import os

import asyncio
import aiohttp

# pip install customtkinter
# pip install pywin32
# pip install requests
# pip install Pillow


# ФУНКЦИИ И ПРОЦЕДУРЫ ОСНОВНОЙ ПРОГРАММЫ


def clear_console():  # Очистка консоли, пока
    # оставлю !
    os.system("cls")

if __name__ == "__main__":
    clear_console()

global WIN32PRINT_AVAILABLE

app = App()

app.mainloop()

