from settings_manager import save_settings_manager, load_settings_manager
from interface_manager import Init_Interface_Settings_manager

import random
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

from tkcalendar import Calendar
from datetime import datetime
from datetime import date

import barcode
from barcode.writer import ImageWriter

from io import BytesIO
from PIL import ImageTk, Image


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
        self.console = None
        self.bar_tender_enable = False
        self.btApp = None

        # Взвешивание
        self.getWeightEnable = False

        self.stable_counter = int(0)
        self.array_weight = list()
        self.stable_weight = 0
        self.data_for_bartender = date.today()
        self.data_for_bartender = self.data_for_bartender.strftime(
            "%d.%m.%Y"
        )  # по умолчанию ставим текущую дату

        self.count_pieces = 0  # счетчки взвешиваний, не может быть больше self.pieces_entry (поле на экране)

        # Всплывающее окно для календаря
        self.calendar_window = None

        # Проверяем доступность win32print в конструкторе
        self.WIN32PRINT_AVAILABLE = self.check_win32print_availability()
        self.available_printers = self.get_available_printers()

        self.Init_Interface_Settings()  # Отрисовка страницы настроек

        self.initialize_bar_tender()  # Инициализация BarTender

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

        # Изменяем цвета фона у фрейма (табло веса)
        self.current_weight_frame.configure(fg_color="#00920C")
        # Переключатель тестовой печати ставим OFF
        self.switch_demo.deselect()

    def getWeightThreading_Disable(self):
        print("Окончание взвешивания.")
        self.getWeightEnable = False
        # Изменяем цвета фона у фрейма (табло веса)
        self.current_weight_frame.configure(fg_color="#000000")

    def switch_demo_printer(self):
        pass

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

    def update_weight_table(self, weight_value, test_mode=False):  # Вставка веса в таблицу

        if self.getWeightEnable and test_mode: #Если режим взвешивания и это тестовый режим
            weight_value = 0
            return
        
        # if self.getWeightEnable != True and test_mode != True: #Если взвешивание не разрешено и это не тестовый режим
        #     weight_value = 0
        #     return

        if weight_value <= float(
            self.zero_threshold.get()
        ):  # Если вес меньше или равен порогу нуля
            self.array_weight.clear()
            self.stable_weight = 0
            return
        
        if test_mode:
            #В тестовом режиме заполняем контейнер этим весом, эмулируя данные с весов
            self.array_weight.clear() # очищаем
            self.array_weight = [weight_value] * int(self.stability_threshold.get()) # Заполняем
            self.stable_weight = weight_value #устанавливаем текущий вес 

        if len(self.array_weight) < float(self.stability_threshold.get()):
            self.array_weight.append(weight_value)
        else:
            # проверка на стабильный вес
            if len((set(self.array_weight))) == 1:

                weight_value = self.array_weight[0]

                rounded_weight = round(weight_value, 2)  # округляем текущий вес
                rounded_stable = round(self.stable_weight, 2)  # округляем текущий вес

                if abs(rounded_stable - rounded_weight) >= 0.05 or rounded_weight == rounded_stable:
                    self.stable_weight = weight_value

                    self.add_to_table(weight_value)  # Выводим вес в таблицу
                    self.activated_barTender_process(
                        weight_value
                    )  # Вызываем бартендер но он в другом потоке

            # Очищаем список
            self.array_weight.clear()

    # Функция вывода веса в таблицу
    def add_to_table(self, weight_value):
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
        self.after(0, lambda: self.launch_bar_tender_in_main_thread(weight_value,))

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

    def browse_btw_file_total(self):
        """Открыть диалог выбора .btw файла"""
        file_path = filedialog.askopenfilename(
            title="Выберите файл шаблона",
            filetypes=[("Файлы шаблонов", "*.btw"), ("Все файлы", "*.*")],
        )

        if file_path and self.validate_btw_file(file_path):
            self.template_entry_total.delete(0, "end")
            self.template_entry_total.insert(0, file_path)

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

    def browse_directory(self, entry_widget):
        """Открыть диалог выбора директории"""
        directory = filedialog.askdirectory(title="Выберите папку")
        if directory:
            entry_widget.delete(0, "end")
            entry_widget.insert(0, directory)

    # Функции работы с таблицей

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
                # messagebox.showinfo("Info", "BarTender уже инициализирован!")
                print("ℹ BarTender уже инициализирован")
                return

            self.btApp = win32.Dispatch("BarTender.Application")
            self.btApp.Visible = False

            self.bar_tender_enable = True
            # messagebox.showinfo("Success", "BarTender успешно инициализирован!")
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

    # region КАЛЕНДАРЬ

    def open_calendar(self):
        if self.calendar_window is None or not self.calendar_window.winfo_exists():
            # Создаем Toplevel окно (из tkinter)
            self.calendar_window = CTk.CTkToplevel(self)
            self.calendar_window.title("Выберите дату")
            self.calendar_window.geometry("400x400")
            self.calendar_window.transient(self)  # Поведение модального окна
            self.calendar_window.grab_set()  # Захватываем фокус

            # Центрируем окно
            self.center_calendar_window()

            # Создаем календарь (из tkcalendar)
            calendar = Calendar(
                self.calendar_window,
                selectmode="day",
                year=datetime.now().year,
                month=datetime.now().month,
                day=datetime.now().day,
                date_pattern="dd.mm.yyyy",
            )
            calendar.pack(pady=20, padx=20, fill="both", expand=True)
            # Кнопка подтверждения выбора
            select_btn = CTk.CTkButton(
                self.calendar_window,
                text="Выбрать",
                hover_color="#C0C0C0",
                command=lambda: self.select_date(calendar),
            )
            select_btn.pack(pady=10)

            # Кнопка отмены
            cancel_btn = CTk.CTkButton(
                self.calendar_window,
                text="Отмена",
                command=self.calendar_window.destroy,
                fg_color="#424242",
                hover_color="#C0C0C0",
                border_width=1,
            )
            cancel_btn.pack(pady=5)
        else:
            self.calendar_window.lift()  # Поднимаем окно поверх других

    def select_date(self, calendar):
        """Обрабатывает выбор даты из календаря"""
        selected_date = calendar.get_date()
        self.data_for_bartender = selected_date

        # self.date_entry.delete(0, "end")
        # self.date_entry.insert(0, selected_date)

        self.calendar_window.destroy()
        self.calendar_window = None

    def center_calendar_window(self):

        # Обновляем геометрию чтобы получить актуальные размеры
        self.calendar_window.update_idletasks()

        # Получаем размеры главного окна
        main_width = self.winfo_width()
        main_height = self.winfo_height()
        main_x = self.winfo_x()
        main_y = self.winfo_y()

        # Получаем размеры окна календаря
        calendar_width = 400
        calendar_height = 400

        # Вычисляем позицию для центрирования относительно главного окна
        x = main_x + (main_width - calendar_width) // 2
        y = main_y + (main_height - calendar_height) // 2

        # Устанавливаем позицию
        self.calendar_window.geometry(f"{calendar_width}x{calendar_height}+{x}+{y}")

    # endregion

    # region ТЕСТОВОЕ ВЗВЕШИВАНИЕ ДЛЯ ШТРИХКОДА
    def generate_weight_test(self):
        kg = random.randint(0, 99)

        # Генерируем граммы от 0 до 999
        grams = random.randint(0, 999)

        weight = f"{kg}.{grams:03d}"

        self.weight_entry_test.delete(0, "end")  # Очищаем поле
        self.weight_entry_test.insert(0, str(weight))  # Вставляем сгенерированный вес

        # Получаем артикул из поля
        article = self.article_entry.get().strip()

        if article:
            # Форматируем вес в 5 цифр: 2 цифры кг + 3 цифры грамм
            weight_for_barcode = f"{kg:02d}{grams:03d}"  # Всегда 5 цифр

            # Прицепляем вес к артикулу
            barcode_data = article + weight_for_barcode

            print(f"Артикул: {article}")
            print(f"Данные для штрих-кода: {barcode_data}")

            # Генерируем штрих-код
            try:
                ean = barcode.get("ean13", barcode_data, writer=ImageWriter())

                buffer = BytesIO()
                ean.write(buffer)
                buffer.seek(0)

                pil_image = Image.open(buffer)
                ctk_image = CTk.CTkImage(
                    light_image=pil_image, dark_image=pil_image, size=(200, 80)
                )

                self.test_barcode_label.configure(image=ctk_image, text="")
                print(f"Штрих-код сгенерирован: {barcode_data}")

                # if self.bar_tender_enable != True:
                #     print("BarTender не активирован.")
                # return
                enable_demo_print = self.switch_demo.get()
                self.launch_bar_tender_in_main_thread(barcode_data, float(weight), self.data_for_bartender, False)
                self.update_weight_table(float(weight), True)

            except Exception as e:
                return

                # print(f"Ошибка генерации штрих-кода: {e}")
                # self.test_barcode_label.configure(text="Ошибка генерации")

            print(f"Вес: {self.weight_entry_test.get()}")

    # endregion

    # region Заполнение шаблона этикетки BARTENDER

    def launch_bar_tender_in_main_thread(self, barcode_data: str, weight: float, data_for_bartender: str, print=False):

        current_dir = os.path.dirname(os.path.abspath(__file__))
        temp_path_jpg = os.path.join(current_dir, "temp.JPG")

        if os.path.exists(temp_path_jpg):
            os.remove(temp_path_jpg)

        template_path = self.template_entry.get()

        name_unit_printer = self.unit_printer_combo.get()

        btFormat = self.btApp.Formats.Open(template_path, False, name_unit_printer)

        # btFormat = self.btApp.Formats.Open(template_path, False, "TSC TE210")
        btFormat.SetNamedSubStringValue("bt_shtrih", barcode_data)
        btFormat.SetNamedSubStringValue("bt_massa", weight)
        btFormat.SetNamedSubStringValue("bt_data", data_for_bartender)

        btFormat.ExportToFile(temp_path_jpg, "JPEG", 1, 300, 1)
        btFormat.IdenticalCopiesOfLabel = 1
        PrintName = "TSC TE210"
        # btFormat.PrintOut(True, False)  # Печать (ShowDialog, WaitUntilCompleted)

        imgShtrih = Image.open(temp_path_jpg)  # Укажите путь к вашему JPG файлу
        imgShtrih = imgShtrih.resize((500, 400))  # Новый размер (ширина, высота)

        # Создаем CTkImage и обновляем существующую метку
        new_photo = CTk.CTkImage(
            light_image=imgShtrih, dark_image=imgShtrih, size=(350, 250)
        )

        # Обновляем изображение в существующей метке
        self.photo.configure(image=new_photo)

    # endregion
