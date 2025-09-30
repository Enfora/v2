from classApp import App

import os


# ФУНКЦИИ И ПРОЦЕДУРЫ ОСНОВНОЙ ПРОГРАММЫ
def clear_console():  # Очистка консоли, пока оставлю !
    os.system("cls")


if __name__ == "__main__":
    clear_console()

app = App()

app.mainloop()
