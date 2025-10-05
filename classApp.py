from settings_manager import save_settings_manager, load_settings_manager
from interface_manager import Init_Interface_Settings_manager


import customtkinter as CTk
import win32print
import tkinter.filedialog as filedialog
import tkinter.messagebox as messagebox
import os
import json
import sys
import time
import win32com.client as win32

import asyncio
import aiohttp
import threading



class SimpleConsole(CTk.CTkTextbox):
    """
    Кастомная консоль для вывода текста
    Наследуется от CTkTextbox и перенаправляет stdout
    """

    def __init__(self, master, **kwargs):
        # Устанавливаем значения по умолчанию
        kwargs.setdefault("fg_color", "black")
        kwargs.setdefault("text_color", "white")
        kwargs.setdefault("font", ("Consolas", 11))
        kwargs.setdefault("wrap", "word")

        super().__init__(master, **kwargs)

        # Сохраняем оригинальный stdout и перенаправляем вывод
        self.old_stdout = sys.stdout
        sys.stdout = self

        # Делаем консоль только для чтения
        self.configure(state="disabled")

    def write(self, text):
        """Перехватывает вывод из print() и добавляет в текстовое поле"""
        self.configure(state="normal")  # Временно включаем редактирование
        self.insert("end", text)
        self.see("end")
        self.configure(state="disabled")  # Снова делаем только для чтения
        self.update_idletasks()  # Обновляем интерфейс

    def flush(self):
        """Требуется для совместимости с sys.stdout"""
        pass

    def clear(self):
        """Очищает консоль"""
        self.configure(state="normal")
        self.delete("1.0", "end")
        self.configure(state="disabled")

    def destroy(self):
        """Восстанавливает оригинальный stdout при уничтожении"""
        sys.stdout = self.old_stdout
        super().destroy()


class App(CTk.CTk):
    def __init__(self):
        super().__init__()

        # BAR TANDER
        self.bar_tender_enable = False
        self.btApp = None

        # Взвешивание
        self.getWeightEnable = False
        
        self.stable_counter = int(0)
        self.array_weight = list()
        self.stable_weight = 0

        # Проверяем доступность win32print в конструкторе
        self.WIN32PRINT_AVAILABLE = self.check_win32print_availability()
        self.available_printers = self.get_available_printers()

        self.Init_Interface_Settings()  # Отрисовка страницы настроек

        if self.WIN32PRINT_AVAILABLE:
            print("⚠ Получение списка принтеров доступно")

        load_settings_manager(self)  # Загружаем настройки

        # Проверяем интервал опроса весов
        self.poll_interval_current = float(1)
        if self.poll_interval.get().strip() == "":
            self.poll_interval_current = float(1)
        else:
            self.poll_interval_current = float(self.poll_interval.get())
        print(f"Интервал опроса весов  = {self.poll_interval_current} сек.")

        # Запускаем мониторинг весов в отдельном потоке
        self.start_weight_monitoring()

    def Init_Interface_Settings(self):
        Init_Interface_Settings_manager(self)
        
    def getWeightThreading_Enable(self):
        print("Старт взвешивания.")
        self.getWeightEnable = True
    
    def getWeightThreading_Disable(self):
        print("Окончание взвешивания.")
        self.getWeightEnable = False

    def start_weight_monitoring(self):
        """Запуск мониторинга весов в отдельном потоке с asyncio"""

        def run_async():
            # Создаем новый event loop для этого потока
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:

                ip_address = self.ip_address.get().strip()

                url = f"http://{ip_address}/rawdata.html"
                loop.run_until_complete(self.basic_get(url))
                
            finally:
                loop.close()

        # Запускаем в отдельном потоке
        thread = threading.Thread(target=run_async, daemon=True)
        thread.start()
        

    async def basic_get(self, url):
        """Асинхронный мониторинг весов"""
        
        async with aiohttp.ClientSession() as session:
            while True:
                try:
                    async with session.get(url, timeout=2) as response:

                        # ✅ Проверяем статус ответа
                        if response.status != 200:
                            print(
                                f"❌ Ошибка HTTP: {response.status} - {response.reason}"
                            )
                            await asyncio.sleep(1)
                            continue

                        # ✅ Получаем и обрабатываем данные
                        data = await response.text()
                        listData = data.strip().split("\n")

                        # ✅ Проверяем что данные не пустые
                        if not listData or not listData[0].strip():
                            print("⚠️ Получены пустые данные от весов")
                            await asyncio.sleep(0.2)
                            continue

                        # ✅ Пытаемся преобразовать в число
                        weight_value = float(listData[0])
                        weight_value = (
                            weight_value if weight_value >= 0 else 0
                        )  # Тернарный оператор
                        # print(f"✅ Вес: {weight_value:.3f}")

                        # Обновляем интерфейс в главном потоке
                        self.update_weight_display(weight_value)
                        self.update_weight_table(weight_value)


                except asyncio.TimeoutError:
                    print("⏰ Таймаут: Весы не ответили за 2 секунды")
                except aiohttp.ClientError as e:
                    print(f"🌐 Ошибка соединения: {e}")
                except ValueError as e:
                    print(f"🔢 Ошибка данных: не могу преобразовать в число")
                except IndexError:
                    print("📋 Ошибка: недостаточно данных в ответе")
                except Exception as e:
                    print(f"⚠️ Неизвестная ошибка: {e}")

                # Задержка перед следующим запросом (даже при ошибках)

                await asyncio.sleep(self.poll_interval_current)

    def update_weight_display(self, weight_value):
        """Обновление отображения веса в интерфейсе"""
        try:
            self.current_weight.configure(text=f"{weight_value:.3f}")
        except Exception as e:
            print(f"Ошибка обновления интерфейса: {e}")

    def update_weight_table (self, weight_value): # Вставка веса в таблицу
        
        if self.getWeightEnable != True:
            weight_value = 0
            return
        
        if weight_value <= float(self.zero_threshold.get()): # Если вес меньше или равен порогу нуля
            self.array_weight.clear()
            self.stable_weight = 0;
            return

        if len(self.array_weight)< float(self.stability_threshold.get()):
            self.array_weight.append(weight_value)
        else:
            #проверка на стабильный вес
            if len((set(self.array_weight))) == 1:

                weight_value = self.array_weight[0]

                rounded_weight = round(weight_value, 2) # округляем текущий вес
                rounded_stable = round(self.stable_weight, 2) # округляем текущий вес

                if abs (rounded_stable - rounded_weight)>=0.05:
                    self.stable_weight = weight_value

                    self.add_to_table (weight_value) # Выводим вес в таблицу
                    self.activated_barTender_process(weight_value) #Вызываем бартендер но он в другом потоке

            # Очищаем список
            self.array_weight.clear()

    # Функция вывода веса в таблицу
    def add_to_table(self,weight_value): 
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        history_entry = f"{timestamp}    {weight_value:.3f} кг\n"

        self.weights_table.configure(state="normal")
        self.weights_table.insert("end", history_entry)
        self.weights_table.see("end")
        self.weights_table.configure(state="disabled")
    
    def activated_barTender_process(self, weight_value):
        """Активация процесса печати - вызов в главном потоке"""
        # Передаем задачу в главный поток
        if self.bar_tender_enable != True:
            print("BarTender не активирован.")
            return
        self.after(0, lambda: self._run_bar_tender_in_main_thread(weight_value))

    def _run_bar_tender_in_main_thread(self, weight_value):
        template_path = self.template_entry.get()
        
        jpg_path = self.jpg_path.get()
        normalized_path_jpg = jpg_path.replace("/", "\\")
        
        temp_path_jpg = normalized_path_jpg + "\\temp_jpg.jpg"
        
        name_unit_printer = self.unit_printer_combo.get()

        btFormat = self.btApp.Formats.Open(template_path, False, name_unit_printer)
        
        btFormat.SetNamedSubStringValue("bt_massa", weight_value)
        btFormat.SetNamedSubStringValue("bt_shtrih", "230076200216")


        btFormat.ExportToFile(temp_path_jpg, "JPEG", 1, 300, 1)
        btFormat.IdenticalCopiesOfLabel = 1 
        PrintName = "TSC TE210"
        btFormat.PrintOut(True, False)  # Печать (ShowDialog, WaitUntilCompleted)

        print (temp_path_jpg)

    # region Вспомогательные ФУНКЦИИ


    def validate_numeric_input(self, new_text):  # Валидация цифр
        """Функция проверяет что ввод содержит только цифры"""
        return new_text.isdigit() or new_text == ""

    def validate_float_input(self, new_text):  # Валидация цифр с точкой
        """Проверяет ввод чисел с плавающей точкой"""
        if new_text == "" or new_text == "-":
            return True
        try:
            float(new_text)
            return True
        except ValueError:
            return False

    def check_win32print_availability(self):
        """Проверяет доступность win32print"""
        try:
            import win32print

            return True
        except ImportError:
            return False

    def get_available_printers(self):  # Получение списка доступных принтеров
        printers = []

        if not self.WIN32PRINT_AVAILABLE:
            print("⚠ Получение списка принтеров недоступно")
            return printers
        try:
            for printer in win32print.EnumPrinters(
                win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS
            ):
                printers.append(printer[2])

            return printers
        except Exception as e:
            return printers

    def browse_btw_file(self):
        """Открыть диалог выбора .btw файла"""
        file_path = filedialog.askopenfilename(
            title="Выберите файл шаблона",
            filetypes=[("Файлы шаблонов", "*.btw"), ("Все файлы", "*.*")],
        )

        if file_path and self.validate_btw_file(file_path):
            self.template_entry.delete(0, "end")
            self.template_entry.insert(0, file_path)

    def validate_btw_file(self, file_path):
        """Проверка, что файл имеет расширение .btw"""
        file_ext = os.path.splitext(file_path)[1].lower()

        if file_ext != ".btw":
            messagebox.showerror("Ошибка", "Файл должен иметь расширение .btw!")
            return False

        if not os.path.isfile(file_path):
            messagebox.showerror("Ошибка", "Файл не существует!")
            return False

        return True

    def browse_directory_pdf(self):
        self.browse_directory(self.pdf_path)

    def browse_directory_jpg(self):
        self.jpg_browse_button._state = "disabled"
        self.browse_directory(self.jpg_path)

    def browse_directory(self, entry_widget):
        """Открыть диалог выбора директории"""
        directory = filedialog.askdirectory(title="Выберите папку")
        if directory:
            entry_widget.delete(0, "end")
            entry_widget.insert(0, directory)

    #Функции работы с таблицей

    def clear_table(self):
        self.weights_table.configure(state="normal")
        self.weights_table.delete("1.0", "end")

        # Добавляем обратно заголовки
        header = "ВРЕМЯ                  ВЕС (кг)\n"
        header += "─────────────────────────────────\n"
        self.weights_table.insert("1.0", header)
        self.weights_table.configure(state="disabled")

        print("Таблица истории очищена")


    # ----------------------------------------------------------------

    # ФУНКЦИИ СОХРАНЕНИЯ НАСТРОЕК, вынесены в отдельный файл
    def save_settings(self):
        save_settings_manager(self)

    def load_settings(self):
        load_settings_manager(self)

    # ФУНКЦИИ ИНИЦИАЛИЗАЦИИ BARTENDER

    def initialize_bar_tender(self):
        """Инициализация BarTender"""
        try:
            if self.bar_tender_enable:
                messagebox.showinfo("Info", "BarTender уже инициализирован!")
                print("ℹ BarTender уже инициализирован")
                return

            self.btApp = win32.Dispatch("BarTender.Application")
            self.btApp.Visible = False

            self.bar_tender_enable = True
            messagebox.showinfo("Success", "BarTender успешно инициализирован!")
            print("✓ BarTender успешно инициализирован")

        except Exception as e:
            self.bar_tender_enable = False
            self.btApp = None
            error_msg = f"Ошибка инициализации BarTender: {str(e)}"
            # messagebox.showerror("Error", error_msg)
            print(f"✗ {error_msg}")

    

    # region ФУНКЦИИ ТЕРМИНАЛА
    def create_console_frame(self, parent):
        """Создает фрейм с консолью и элементами управления"""
        # Главный фрейм
        main_frame = CTk.CTkFrame(parent)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Фрейм для кнопок
        button_frame = CTk.CTkFrame(main_frame)
        button_frame.pack(fill="x", padx=5, pady=5)

        # Кнопка очистки консоли
        clear_btn = CTk.CTkButton(
            button_frame, text="Очистить консоль", command=self.clear_console, width=120
        )
        clear_btn.pack(side="left", padx=5)

        # Кнопка тестового вывода
        test_btn = CTk.CTkButton(
            button_frame, text="Версия", command=self.version_console_output, width=120
        )
        test_btn.pack(side="left", padx=5)

        # Создаем консоль
        self.console = SimpleConsole(main_frame, height=400)
        self.console.pack(fill="both", expand=True, padx=5, pady=5)

        return main_frame

    def clear_console(self):
        """Очищает консоль"""
        if hasattr(self, "console"):
            self.console.clear()
            print("Консоль очищена")

    def version_console_output(self):
        """Тестовый вывод в консоль"""
        print("=" * 50)
        print("ТЕСТОВЫЙ ВЫВОД В КОНСОЛЬ")
        print(
            f"Время: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        print("Это сообщение выведено через print()")
        print("Версия программы: v.1, enfora@mail.ru")
        print("=" * 50)

    # endregion
