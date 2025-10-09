import win32com.client as win32
import os
import subprocess
import tkinter

from PIL import ImageTk, Image  # Необходимо установить Pillow: pip install pillow

root = tkinter.Tk()

# создаем рабочую область
frame = tkinter.Frame(root)
frame.grid()

frame_pack = tkinter.Frame(root)

# вставляем кнопку
but = tkinter.Button(frame, text="Кнопка").grid(row=1, column=2)


# os.system('cls||clear')
# Путь к шаблону и выходному PDF
template_path = r"C:\\learn\\v2\\files\\ФаршДОМАШНИЙ.btw"


# Инициализация BarTender
btApp = win32.Dispatch("BarTender.Application")
btApp.Visible = False  # Скрытый режим

# try:
btFormat = btApp.Formats.Open(template_path, False, "TSC TE210")
btFormat.SetNamedSubStringValue("bt_shtrih", "250099915050")
btFormat.SetNamedSubStringValue("bt_massa", "15.050")

# btFormat.ExportToPDF(output_pdf, False, "")  # False = не показывать диалог
# print(f"PDF успешно сохранен: {output_pdf}")

# Экспорт в PNG (можно заменить на JPEG, TIFF, BMP)
# btFormat.ExportToImage(output_image, "PNG")  # Формат: "PNG", "JPEG", "BMP", и т.д.



current_dir = os.path.dirname(os.path.abspath(__file__))
temp_path_jpg = os.path.join(current_dir, "temp.JPG")

if os.path.exists(temp_path_jpg):
    os.remove(temp_path_jpg)

btFormat.ExportToFile(temp_path_jpg, "JPEG", 1, 300, 1)
btFormat.IdenticalCopiesOfLabel = 1
PrintName = "TSC TE210"
# btFormat.PrintOut(True, False)  # Печать (ShowDialog, WaitUntilCompleted)
# btFormat.PrintOut(True, False)  # Печать (ShowDialog, WaitUntilCompleted)
# btFormat.PrintOut(True, False)  # Печать (ShowDialog, WaitUntilCompleted)

# except Exception as e:
#    print(f"Ошибка: {e}")

# finally:


# img = Image.open("C:\\learn\\v2\\temp.JPG")  # Укажите путь к вашему JPG файлу
# img = img.resize((500, 400))  # Новый размер (ширина, высота)

# # Конвертируем изображение для Tkinter
# photo = ImageTk.PhotoImage(img)

# #Добавим метку
# label       = tkinter.Label(frame, text="Hello, World!").grid(row=1,column=1)
# image_label = tkinter.Label(frame, image=photo)

# image_label.grid()

# # 4. Важно: сохраняем ссылку на изображение!
# image_label.image = photo


btFormat.Close(0)  # Закрыть шаблон без сохранения # 1 = btDoNotSaveChanges
# btApp.Quit(1)  # Закрыть BarTender


print("Test")
root.mainloop()
