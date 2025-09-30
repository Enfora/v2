from classApp import App

import os

#pip install customtkinter
#pip install pywin32
#pip install requests
#pip install Pillow



# ФУНКЦИИ И ПРОЦЕДУРЫ ОСНОВНОЙ ПРОГРАММЫ
def clear_console():  # Очистка консоли, пока оставлю !
    os.system("cls")

if __name__ == "__main__":
    clear_console()

app = App()

app.mainloop()
