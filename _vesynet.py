import os
import platform
import json
import customtkinter as CTk
from tkinter import filedialog, messagebox
import win32com.client as win32
import requests
import threading
import subprocess
import sys
import random
from PIL import Image


# import datetime
import time


class ScaleThread(threading.Thread):
    def __init__(
        self, ip_address, stability_threshold=5, poll_interval=0.1, zero_threshold=2.0
    ):
        super().__init__()
        self.ip_address = ip_address
        self.stability_threshold = stability_threshold  # Порог стабилизации, количество после которого считаем вес стабилизированным
        self.poll_interval = poll_interval  # Интервал опроса (секунды)
        self.zero_threshold = zero_threshold  # Порог нуля (граммы) стандартно 2 гр.

        self.url = f"http://{ip_address}/rawdata.html"
        self.stop_requested = False
        self.daemon = True

        # Переменные для стабилизации
        self.current_weight = None  # текущий вес
        self.stable_counter = 0
        self.last_reported = None
        self.was_zero = True

    def stop(self):
        self.stop_requested = True

    def run(self):
        print(f"Весы {self.ip_address} запущены")
        print(f"Порог стабилизации: {self.stability_threshold} измерений")
        print(f"Интервал опроса: {self.poll_interval} секунд")
        print(f"Порог нуля: {self.zero_threshold}г")
        print("Ожидание стабильных показаний...")
        print("Для выхода нажмите Ctrl+C\n")

        while not self.stop_requested:
            try:
                # Получаем данные
                response = requests.get(self.url, timeout=1)
                data = response.text.strip().split("\n")

                if data and data[0].strip():
                    weight_kg = float(data[0].strip())
                    weight_grams = weight_kg * 1000

                    # Определяем статус
                    if self._is_zero_weight(weight_grams):
                        status = "НОЛЬ"
                    else:
                        status = "ВЕС"
                    print(
                        f"Текущий: {weight_grams:.1f}г ({status}), Счетчик: {self.stable_counter}/{self.stability_threshold}",
                        end="\r",
                    )

                    # Проверка стабилизации
                    if self._check_stability(weight_grams):
                        print(f"\nСТАБИЛЬНЫЙ ВЕС: {weight_grams:.1f} г")

            except Exception as e:
                print(f"Ошибка: {e}")

            time.sleep(self.poll_interval)  # Используем настраиваемый интервал

    def _is_zero_weight(self, weight):
        """Проверяет, считается ли вес нулевым."""
        return weight < self.zero_threshold

    def _check_stability(self, new_weight):
        """
        Проверяет стабилизацию веса с учетом прохода через ноль.
        """

        # 1. Проверка нулевого состояния
        if self._is_zero_weight(new_weight):
            if not self.was_zero:
                print("\nОбнаружен проход через 0 - сброс состояния")
                self.was_zero = True
            self.current_weight = None
            self.stable_counter = 0
            return False

        # 2. Обнаружение нового товара после нуля
        if self.was_zero:
            print("\nОбнаружен новый товар после нуля")
            self.was_zero = False
            self.current_weight = new_weight
            self.stable_counter = 1
            self.last_reported = None
            return False

        # 3. Проверка стабильности веса
        if (
            self.current_weight is not None
            and abs(self.current_weight - new_weight) < 0.1
        ):
            self.stable_counter += 1
        else:
            self.current_weight = new_weight
            self.stable_counter = 1
            return False

        # 4. Проверка порога стабилизации (используем настраиваемое значение)
        if self.stable_counter >= self.stability_threshold:
            if self.last_reported != new_weight:
                self.last_reported = new_weight
                return True

        return False


class App(CTk.CTk):
    def __init__(self):
        super().__init__()

        # Геометрия и название программы
        self.geometry("1024x768")
        self.resizable = (False, False)  # type: ignore
        self.title("Оболочка для сетевых весов. Enfora@2025")

        # Создаем вкладки TabView
        self.tabview = CTk.CTkTabview(self)
        self.tabview.pack(padx=10, pady=10, fill="both", expand=True)

        """Создание вкладок"""
        self.tab_workarea = self.tabview.add("Рабочая область")
        self.tab_settings = self.tabview.add("Настройки")

        self.available_printers = (
            self.get_available_printers()
        )  # Получение списка принтеров
        self.setup_settings_tab()  # Страница установок
        self.setup_event_handlers()  # Установка привязки кнопок

        self.setup_workarea_tab()  # рабочая область
        self.setup_weights_table()  # Таблица с историей веса

        self.ScaleThread = None  # пока нет потока

    def setup_settings_tab(self):
        """Настройка вкладки Области настроек"""
        # Заголовок
        CTk.CTkLabel(
            self.tab_settings,
            text="Общие настройки весов и шаблонов",
            font=CTk.CTkFont(size=16, weight="bold"),
        ).pack(pady=10)

        # Фрейм для кнопок сохранения/загрузки вверху слева
        button_frame = CTk.CTkFrame(
            self.tab_settings, fg_color="transparent", height=40
        )
        button_frame.pack(side="top", anchor="nw", fill="x", pady=(0, 10), padx=10)

        self.save_button = CTk.CTkButton(  # Кнопка Сохранить настройки
            button_frame,
            text="Сохранить настройки",
            width=120,
            command=self.save_settings,
        )
        self.save_button.pack(side="left", padx=(0, 10))

        self.load_button = CTk.CTkButton(  # Кнопка Загрузить настройки
            button_frame,
            text="Загрузить настройки",
            width=120,
            command=self.load_settings,
        )
        self.load_button.pack(side="left")

        # Фрейм для области настроек
        setting_frame = CTk.CTkFrame(self.tab_settings, fg_color="lightgrey")
        setting_frame.pack(side="top", fill="both", expand=True, pady=5, padx=10)

        # -------------------------------- Фрейм для ввода к шаблону этикетки ---------------------------
        # Подзаголовок
        CTk.CTkLabel(
            setting_frame,
            text="Путь к шаблону этикетки (только .btw файлы):",
            font=CTk.CTkFont(weight="bold"),
        ).pack(anchor="w", padx=10, pady=(10, 0))

        # Фрейм для поля ввода и кнопки
        input_frame = CTk.CTkFrame(setting_frame, fg_color="transparent")
        input_frame.pack(fill="x", padx=10, pady=(5, 10))

        # Поле ввода для пути к .btw файлу
        self.template_entry = CTk.CTkEntry(
            input_frame, placeholder_text="Выберите файл .btw...", height=35
        )
        self.template_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        # Кнопка выбора файла
        self.btw_browse_button = CTk.CTkButton(input_frame, text="Обзор...", width=100)
        self.btw_browse_button.pack(side="right")

        # Кнопка открытия BarTender
        self.run_bartender_button = CTk.CTkButton(
            input_frame,
            text="Редактор",
            width=120,
            height=35,
            font=CTk.CTkFont(size=12, weight="bold"),
            command=self.run_bartender,
        )
        self.run_bartender_button.pack(side="right", padx=(0, 10))

        # Фрейм для экспорта в PDF
        pdf_frame = CTk.CTkFrame(setting_frame, fg_color="transparent")
        pdf_frame.pack(fill="x", padx=10, pady=(5, 10))

        # Чекбокс, путь к файлу, кнопка выбора каталога PDF
        self.checkbox_pdf = CTk.CTkCheckBox(
            pdf_frame,
            text="Запись в pdf",
            hover=True,
            border_width=2,
            bg_color="transparent",
            corner_radius=5,
            border_color="blue",
        )
        self.checkbox_pdf.pack(side="left", padx=(5, 5))

        self.pdf_entry = CTk.CTkEntry(
            pdf_frame, placeholder_text="Укажите путь к каталогу pdf", height=35
        )
        self.pdf_entry.pack(side="left", fill="x", expand=True, padx=(5, 10))
        self.pdf_browse_button = CTk.CTkButton(pdf_frame, text="Обзор...", width=100)
        self.pdf_browse_button.pack(side="right")

        # Фрейм для экспорта в PNG
        png_frame = CTk.CTkFrame(setting_frame, fg_color="transparent")
        png_frame.pack(fill="x", padx=10, pady=(5, 10))

        # Чекбокс, путь к файлу, кнопка выбора каталога PNG
        self.checkbox_png = CTk.CTkCheckBox(
            png_frame,
            text="Запись в png",
            hover=True,
            border_width=2,
            bg_color="transparent",
            corner_radius=5,
            border_color="blue",
        )
        self.checkbox_png.pack(side="left", padx=(5, 5))
        self.png_entry = CTk.CTkEntry(
            png_frame, placeholder_text="Укажите путь к каталогу png", height=35
        )
        self.png_entry.pack(side="left", fill="x", expand=True, padx=(5, 10))
        self.png_browse_button = CTk.CTkButton(png_frame, text="Обзор...", width=100)
        self.png_browse_button.pack(side="right")

        # Фрейм для экспорта в JPG
        jpg_frame = CTk.CTkFrame(setting_frame, fg_color="transparent")
        jpg_frame.pack(fill="x", padx=10, pady=(5, 10))

        # Чекбокс, путь к файлу, кнопка выбора каталога JPG
        self.checkbox_jpg = CTk.CTkCheckBox(
            jpg_frame,
            text="Запись в jpg",
            hover=True,
            border_width=2,
            bg_color="transparent",
            corner_radius=5,
            border_color="blue",
        )
        self.checkbox_jpg.pack(side="left", padx=(5, 5))
        self.jpg_entry = CTk.CTkEntry(
            jpg_frame, placeholder_text="Укажите путь к каталогу jpg", height=35
        )
        self.jpg_entry.pack(side="left", fill="x", expand=True, padx=(5, 10))
        self.jpg_browse_button = CTk.CTkButton(jpg_frame, text="Обзор...", width=100)
        self.jpg_browse_button.pack(side="right")

        # -------------------------------- Фрейм для ввода IP адреса ---------------------------
        # Подзаголовок для IP адреса
        CTk.CTkLabel(
            setting_frame,
            text="Настройки весов (IP адрес, определение стабильного веса, интервал опроса весов, порог нуля (г.)):",
            font=CTk.CTkFont(weight="bold"),
        ).pack(anchor="w", padx=10, pady=(20, 0))

        # Фрейм для поля ввода IP адреса
        ip_frame = CTk.CTkFrame(setting_frame, fg_color="transparent")
        ip_frame.pack(fill="x", padx=10, pady=(5, 10))

        # Поле ввода для IP адреса с маской
        self.ip_address = CTk.CTkEntry(
            ip_frame,
            placeholder_text="Введите IP адрес весов (например: 192.168.1.100/24)...",
            height=35,
        )
        self.ip_address.pack(side="left", fill="x", expand=True, padx=(0, 10))

        # Поле для ввода stability_threshold - Количество стабильных взвешиваний
        vcmd = (self.register(self.validate_numeric_input), "%P")
        self.stability_threshold = CTk.CTkEntry(
            ip_frame,
            validate="key",
            validatecommand=vcmd,
            placeholder_text="Кол-во взвешиваний для опред. стабильности",
            height=35,
        )
        self.stability_threshold.pack(side="left", fill="x", expand=True, padx=(0, 10))

        # Поле для ввода poll_interval - Интервал опроса весов
        vcmd = (self.register(self.validate_float_input), "%P")
        self.poll_interval = CTk.CTkEntry(
            ip_frame,
            validate="key",
            validatecommand=vcmd,
            placeholder_text="Интервал опроса весов, с",
            height=35,
        )
        self.poll_interval.pack(side="left", fill="x", expand=True, padx=(0, 10))

        # Поле для ввода zero_threshold - Порог нуля
        vcmd = (self.register(self.validate_numeric_input), "%P")
        self.zero_threshold = CTk.CTkEntry(
            ip_frame,
            validate="key",
            validatecommand=vcmd,
            placeholder_text="Порог нуля, г.",
            height=35,
        )
        self.zero_threshold.pack(side="left", fill="x", expand=True, padx=(0, 10))

        # -------------------------------- Фрейм для количества штук в пачке ---------------------------
        # Подзаголовок для количества штук
        CTk.CTkLabel(
            setting_frame,
            text="Количество штук в пачке:",
            font=CTk.CTkFont(weight="bold"),
        ).pack(anchor="w", padx=10, pady=(20, 0))

        # Фрейм для поля ввода количества штук
        pieces_frame = CTk.CTkFrame(setting_frame, fg_color="transparent")
        pieces_frame.pack(fill="x", padx=10, pady=(5, 10))

        # Поле ввода для количества штук в пачке
        vcmd = (self.register(self.validate_numeric_input), "%P")
        self.pieces_entry = CTk.CTkEntry(
            pieces_frame,
            validate="key",
            validatecommand=vcmd,
            placeholder_text="Введите количество штук в пачке (например: 12)...",
            height=35,
        )
        self.pieces_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        # -------------------------------- Фрейм для принтеров ---------------------------
        # Подзаголовок для принтеров
        CTk.CTkLabel(
            setting_frame,
            text="Настройки принтеров:",
            font=CTk.CTkFont(weight="bold"),
        ).pack(anchor="w", padx=10, pady=(20, 0))

        # Фрейм для принтера штучной этикетки
        unit_printer_frame = CTk.CTkFrame(setting_frame, fg_color="transparent")
        unit_printer_frame.pack(fill="x", padx=10, pady=(5, 5))

        CTk.CTkLabel(
            unit_printer_frame,
            text="Принтер штучной этикетки:",
            font=CTk.CTkFont(weight="bold"),
        ).pack(anchor="w", side="left", padx=(0, 10))

        # Выпадающий список для принтера штучной этикетки
        self.unit_printer_combo = CTk.CTkComboBox(
            unit_printer_frame,
            values=self.available_printers,
            height=35,
            width=300,
            state="normal",
            hover=True,
        )
        self.unit_printer_combo.pack(side="left", fill="x", expand=True)

        # Фрейм для принтера общей этикетки
        total_printer_frame = CTk.CTkFrame(setting_frame, fg_color="transparent")
        total_printer_frame.pack(fill="x", padx=10, pady=(5, 10))

        CTk.CTkLabel(
            total_printer_frame,
            text="Принтер общей этикетки:",
            font=CTk.CTkFont(weight="bold"),
        ).pack(anchor="w", side="left", padx=(0, 10))

        # Выпадающий список для принтера общей этикетки
        self.total_printer_combo = CTk.CTkComboBox(
            total_printer_frame,
            values=self.available_printers,
            height=35,
            width=300,
            state="normal",
        )
        self.total_printer_combo.pack(side="left", fill="x", expand=True)

    def setup_workarea_tab(self):
        self.bar_tender_enable = False
        self.btApp = None
        # Фрейм для кнопки вверху слева
        button_frame = CTk.CTkFrame(
            self.tab_workarea, fg_color="transparent", height=40
        )
        button_frame.pack(side="top", anchor="nw", fill="x", pady=(0, 10), padx=10)

        # Кнопка для выполнения действия вверху слева
        self.action_button = CTk.CTkButton(
            button_frame,
            text="Инициализация BarTender",
            width=120,
            height=35,
            font=CTk.CTkFont(size=12, weight="bold"),
            command=self.initialize_bar_tender,
        )
        self.action_button.pack(side="left", padx=(0, 10))

        # Кнопка начать взвешивание
        self.start_button = CTk.CTkButton(
            button_frame,
            text="Начать взвешивание",
            width=120,
            height=35,
            font=CTk.CTkFont(size=12, weight="bold"),
            # command=self.getWeightThreading,
        )
        self.start_button.pack(side="left", padx=(0, 10))

        # Кнопка остановить взвешивание
        self.stop_button = CTk.CTkButton(
            button_frame,
            text="Остановить взвешивание",
            width=120,
            height=35,
            font=CTk.CTkFont(size=12, weight="bold"),
            # command=self.stopWeightThreading,
            # state="disabled",
        )
        self.stop_button.pack(side="left", padx=(0, 10))

        # Кнопка тестовое взвешивание
        self.test_button = CTk.CTkButton(
            button_frame,
            text="Тест",
            width=120,
            height=35,
            font=CTk.CTkFont(size=12, weight="bold"),
            command=self.test,
        )
        self.test_button.pack(side="left", padx=(0, 10))

        # Кнопка очистки таблицы
        self.clear_button_table = CTk.CTkButton(
            button_frame,
            text="Очистка таблицы",
            width=120,
            height=35,
            font=CTk.CTkFont(size=12, weight="bold"),
            command=self.clear_table,
        )
        self.clear_button_table.pack(side="left", padx=(0, 10))

        # Фрейм для вывода текущего веса
        self.current_weight_frame = CTk.CTkFrame(
            self.tab_workarea,
            height=100,
            fg_color="black",
            corner_radius=10,
        )
        self.current_weight_frame.pack(side="top", fill="x", padx=10, pady=10)

        # Поле для отображения веса
        self.current_weight = CTk.CTkLabel(
            self.current_weight_frame,
            text="0.000 кг",
            font=CTk.CTkFont(family="Digital-7 Mono", size=100),
            text_color="#00FF00",
            fg_color="black",
            bg_color="black",
        )
        self.current_weight.pack(expand=True, fill="both", padx=20, pady=20)

    def clear_table(self):
        self.weights_table.configure(state="normal")
        self.weights_table.delete("1.0", "end")

        # Добавляем обратно заголовки
        header = "ВРЕМЯ                  ВЕС (кг)\n"
        header += "─────────────────────────────────\n"
        self.weights_table.insert("1.0", header)
        self.weights_table.configure(state="disabled")

    print("Таблица истории очищена")

    def test(self):
        # Отключаем кнопку
        self.test_button.configure(state="disabled")

        test_weight = random.uniform(10, 50)
        self.current_weight.configure(text=f"{test_weight:.3f} кг")
        # Добавляем запись в историю
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        history_entry = f"{timestamp}    {test_weight:.3f} кг\n"

        self.weights_table.configure(state="normal")
        self.weights_table.insert("end", history_entry)
        self.weights_table.see("end")
        self.weights_table.configure(state="disabled")

        # включаем кнопку
        self.test_button.configure(state="normal")
        self.start_barTender_process(test_weight)

    def start_barTender_process(self, test_weight):
        template_path = self.template_entry.get()

        pathJpg = self.jpg_entry.get()
        normalized_path_jpg = pathJpg.replace("/", "\\")
        temp_path_jpg = normalized_path_jpg + "\\temp_jpg.jpg"

        btFormat = self.btApp.Formats.Open(template_path, False, "TSC TE210")  # type: ignore
        btFormat.SetNamedSubStringValue("bt_massa", test_weight)

        if os.path.exists(temp_path_jpg):
            os.remove(temp_path_jpg)

        btFormat.ExportToFile(temp_path_jpg, "JPEG", 1, 300, 1)

        imagePhoto = CTk.CTkImage(
            light_image=Image.open(temp_path_jpg), size=(200, 150)
        )
        self.photo.configure(image=imagePhoto)

    def run_bartender(self):
        template_path = self.template_entry.get()
        if not template_path:
            messagebox.showerror("Ошибка", "Укажите путь к шаблону!")
            return
        if not os.path.exists(template_path):
            messagebox.showerror("Ошибка", "Файл шаблона не существует!")
            return

        def open_file_thread():
            try:
                os.startfile(template_path)
            except Exception as e:
                # Выводим ошибку в основном потоке
                self.after(
                    0,
                    lambda: messagebox.showerror(
                        "Ошибка", f"Ошибка запуска BarTender: {str(e)}"
                    ),
                )
            else:
                # Показываем сообщение об успехе в основном потоке
                self.after(0, lambda: messagebox.showinfo("Успех", "Запуск BarTender."))

        threading.Thread(target=open_file_thread, daemon=True).start()

    def setup_weights_table(self):
        """Настройка таблицы с историей весов"""
        # Фрейм для таблицы
        table_frame = CTk.CTkFrame(self.tab_workarea)
        table_frame.pack(side="top", fill="both", expand=True, padx=10, pady=10)

        # Заголовок таблицы
        CTk.CTkLabel(
            table_frame,
            text="ИСТОРИЯ ВЗВЕШИВАНИЙ",
            font=CTk.CTkFont(size=14, weight="bold"),
        ).pack(pady=(10, 5))

        basemente_frame = CTk.CTkFrame(table_frame, bg_color="red")
        basemente_frame.pack(side="top", fill="both", expand=True, padx=10, pady=10)

        # Создаем таблицу (Treeview)
        self.weights_table = CTk.CTkTextbox(
            basemente_frame,
            height=200,
            font=CTk.CTkFont(
                family="Consolas", size=14
            ),  # Моноширинный шрифт для таблицы
        )
        self.weights_table.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        # Фрейм для фото (чтобы лучше контролировать отступы)
        photo_frame = CTk.CTkFrame(basemente_frame)
        photo_frame.pack(side="right", fill="both", expand=True, padx=(5, 10), pady=10)

        self.photo = CTk.CTkLabel(photo_frame, text="", fg_color="transparent")
        self.photo.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        # Добавляем заголовки колонок
        header = "ВРЕМЯ                  ВЕС (кг)\n"
        header += "─────────────────────────────────\n"
        self.weights_table.insert("1.0", header)
        self.weights_table.configure(state="disabled")  # Делаем только для чтения

    def validate_float_input(self, new_text):
        """Проверяет ввод чисел с плавающей точкой"""
        if new_text == "" or new_text == "-":
            return True
        try:
            float(new_text)
            return True
        except ValueError:
            return False

    def validate_numeric_input(self, new_text):
        """Проверяет, что ввод содержит только цифры"""
        return new_text.isdigit() or new_text == ""

    def setup_event_handlers(self):
        """Настройка обработчиков событий для кнопок"""
        self.btw_browse_button.configure(command=self.browse_btw_file)
        self.pdf_browse_button.configure(
            command=lambda: self.browse_directory(self.pdf_entry)
        )
        self.png_browse_button.configure(
            command=lambda: self.browse_directory(self.png_entry)
        )
        self.jpg_browse_button.configure(
            command=lambda: self.browse_directory(self.jpg_entry)
        )

    def browse_btw_file(self):
        """Открыть диалог выбора .btw файла"""
        file_path = filedialog.askopenfilename(
            title="Выберите файл шаблона",
            filetypes=[("Файлы шаблонов", "*.btw"), ("Все файлы", "*.*")],
        )

        if file_path and self.validate_btw_file(file_path):
            self.template_entry.delete(0, "end")
            self.template_entry.insert(0, file_path)

    def browse_directory(self, entry_widget):
        """Открыть диалог выбора директории"""
        directory = filedialog.askdirectory(title="Выберите папку")
        if directory:
            entry_widget.delete(0, "end")
            entry_widget.insert(0, directory)

    def validate_btw_file(self, file_path):
        """Проверка, что файл имеет расширение .btw"""
        file_ext = os.path.splitext(file_path)[1].lower()

        if file_ext != ".btw":
            messagebox.showerror("Ошибка", "Файл должен иметь расширение .btw!")
            return False

        if not os.path.isfile(file_path):
            messagebox.showerror("Ошибка", "Файл не существует!")
            return False

        if os.path.getsize(file_path) > 50 * 1024 * 1024:
            messagebox.showerror("Ошибка", "Файл слишком большой! Максимум 50MB.")
            return False

        return True

    def get_available_printers(self):  # Получение списка доступных принтеров
        printers = []

        if not WIN32PRINT_AVAILABLE:
            print("⚠ Получение списка принтеров недоступно")
            return printers
        try:
            for printer in win32print.EnumPrinters(
                win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS
            ):
                printers.append(printer[2])
            print(f"✓ Найдено принтеров: {len(printers)}")
            return printers
        except Exception as e:
            print(f"✗ Ошибка получения списка принтеров: {e}")
            return printers

    def save_settings(self):  # Запоминаем настройки в JSON
        """Сохранение настроек в JSON файл"""
        settings = {
            "checkbox_jpg": bool(self.checkbox_jpg.get()),
            "checkbox_pdf": bool(self.checkbox_pdf.get()),
            "checkbox_png": bool(self.checkbox_png.get()),
            "jpg_entry": self.jpg_entry.get(),
            "pdf_entry": self.pdf_entry.get(),
            "png_entry": self.png_entry.get(),
            "template_entry": self.template_entry.get(),
            "ip_address": self.ip_address.get(),
            "pieces_entry": self.pieces_entry.get(),
            "unit_printer": self.unit_printer_combo.get(),
            "total_printer": self.total_printer_combo.get(),
            "stability_threshold": self.stability_threshold.get(),
            "poll_interval": self.poll_interval.get(),
            "zero_threshold": self.zero_threshold.get(),
        }

        try:
            with open("settings.json", "w", encoding="utf-8") as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
            # messagebox.showinfo("Успех", "Настройки успешно сохранены в settings.json")
            print("✓ Настройки успешно сохранены в settings.json")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить настройки: {e}")
            print(f"✗ Ошибка сохранения настроек: {e}")

    def load_settings(self):
        """Загрузка настроек из JSON файла"""
        try:
            if not os.path.exists("settings.json"):
                messagebox.showinfo("Информация", "Файл настроек не найден.")
                print(
                    "ℹ Файл настроек не найден. Будут использованы настройки по умолчанию."
                )
                return

            with open("settings.json", "r", encoding="utf-8") as f:
                settings = json.load(f)

            # Заполняем поля ввода
            self.template_entry.delete(0, "end")
            self.template_entry.insert(0, settings.get("template_entry", ""))

            self.pdf_entry.delete(0, "end")
            self.pdf_entry.insert(0, settings.get("pdf_entry", ""))

            self.png_entry.delete(0, "end")
            self.png_entry.insert(0, settings.get("png_entry", ""))

            self.jpg_entry.delete(0, "end")
            self.jpg_entry.insert(0, settings.get("jpg_entry", ""))

            # Заполняем поле IP адреса
            self.ip_address.delete(0, "end")
            self.ip_address.insert(0, settings.get("ip_address", ""))

            # Заполняем поле количества штук в пачке
            self.pieces_entry.delete(0, "end")
            self.pieces_entry.insert(0, settings.get("pieces_entry", ""))

            # Стабильность взвешиваний
            self.stability_threshold.delete(0, "end")
            self.stability_threshold.insert(0, settings.get("stability_threshold", ""))

            # Интервал опроса весов
            self.poll_interval.delete(0, "end")
            self.poll_interval.insert(0, settings.get("poll_interval", ""))

            # Порог нуля
            self.zero_threshold.delete(0, "end")
            self.zero_threshold.insert(0, settings.get("zero_threshold", ""))

            # Заполняем выпадающие списки принтеров
            unit_printer = settings.get("unit_printer", "")
            if unit_printer in self.available_printers:
                self.unit_printer_combo.set(unit_printer)
            elif self.available_printers:
                self.unit_printer_combo.set(self.available_printers[0])

            total_printer = settings.get("total_printer", "")
            if total_printer in self.available_printers:
                self.total_printer_combo.set(total_printer)
            elif self.available_printers:
                self.total_printer_combo.set(self.available_printers[0])

            # Устанавливаем чекбоксы
            if settings.get("checkbox_pdf", False):
                self.checkbox_pdf.select()
            else:
                self.checkbox_pdf.deselect()

            if settings.get("checkbox_png", False):
                self.checkbox_png.select()
            else:
                self.checkbox_png.deselect()

            if settings.get("checkbox_jpg", False):
                self.checkbox_jpg.select()
            else:
                self.checkbox_jpg.deselect()

            # messagebox.showinfo("Успех", "Настройки успешно загружены")
            print("✓ Настройки успешно загружены из settings.json")

        except json.JSONDecodeError:
            messagebox.showerror(
                "Ошибка", "Файл настроек поврежден или имеет неверный формат."
            )
            print("✗ Ошибка: Файл настроек поврежден или имеет неверный формат.")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить настройки: {e}")
            print(f"✗ Ошибка загрузки настроек: {e}")

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
            messagebox.showerror("Error", error_msg)
            print(f"✗ {error_msg}")


# ФУНКЦИИ И ПРОЦЕДУРЫ ОСНОВНОЙ ПРОГРАММЫ
def clear_console():  # Очистка консоли
    os.system("cls")


if __name__ == "__main__":
    clear_console()

    if platform.system() == "Windows":
        try:
            import win32print

            WIN32PRINT_AVAILABLE = True
            print("⚠ Библиотека win32print установлена. Доступен список принтеров.")
        except ImportError:
            WIN32PRINT_AVAILABLE = False
            print("⚠ Библиотека win32print не установлена. Принтеры недоступны.")
    else:
        WIN32PRINT_AVAILABLE = False
        print("⚠ Получение списка принтеров доступно только в Windows")

    CTk.set_appearance_mode("System")
    CTk.set_default_color_theme("blue")

    app = App()

    app.load_settings()
    app.mainloop()
