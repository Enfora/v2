import customtkinter as CTk
import win32print
import tkinter.filedialog as filedialog
import tkinter.messagebox as messagebox
import os



class App(CTk.CTk):
    def __init__(self):
        super().__init__()

        # Проверяем доступность win32print в конструкторе
        self.WIN32PRINT_AVAILABLE = self.check_win32print_availability()
        self.available_printers = self.get_available_printers()

        self.Init_Interface()

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

            print("✓ Модуль win32print доступен")
            return True
        except ImportError:
            print("⚠ Модуль win32print не установлен. Установите: pip install pywin32")
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
            print(f"✓ Найдено принтеров: {len(printers)}")
            return printers
        except Exception as e:
            print(f"✗ Ошибка получения списка принтеров: {e}")
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
            f=1
    
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
    # endregion

    def Init_Interface(self):

        # region НАЧАЛЬНЫЕ УСТАНОВКИ ОКНА
        CTk.set_appearance_mode("Light")  # "Dark", "Light", "System"
        CTk.set_default_color_theme("dark-blue")  # "blue", "green", "dark-blue"

        # region Окно и заголовок программы
        self.geometry("1024x768")
        self.resizable = (False, False)  # type: ignore
        self.title("Оболочка для сетевых весов. Enfora@2025")
        # endregion

        # Создаем вкладки TabView
        tabview = CTk.CTkTabview(self)
        tabview.pack(padx=10, pady=10, fill="both", expand=True)

        """Создание вкладок"""
        tab_workarea = tabview.add("Рабочая область")
        tab_settings = tabview.add("Настройки")

        # Заголовок
        CTk.CTkLabel(
            tab_settings,
            text="Общие настройки весов и шаблонов",
            font=CTk.CTkFont(size=16, weight="bold"),
        ).pack(pady=10)
        # endregion

        # region КНОПКИ СОХРАНЕНИЯ НАСТРОЕК
        frameButtons = CTk.CTkFrame(
            tab_settings, fg_color="transparent", bg_color="lightgray", height=40
        )
        frameButtons.pack(side="top", anchor="nw", fill="x", pady=(0, 10), padx=10)

        save_button = CTk.CTkButton(  # Кнопка Сохранить настройки
            frameButtons,
            text="Сохранить настройки",
            width=120,
            # command=self.save_settings,
        )
        save_button.pack(side="left", padx=(0, 10))

        load_button = CTk.CTkButton(  # Кнопка Загрузить настройки
            frameButtons,
            text="Загрузить настройки",
            width=120,
            # command=self.load_settings,
        )
        load_button.pack(side="left")
        # endregion

        # Фрейм для области настроек
        setting_frame = CTk.CTkFrame(tab_settings, fg_color="lightgrey")
        setting_frame.pack(side="top", fill="both", expand=True, pady=5, padx=10)

        # region BarTender файл
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
        btw_browse_button = CTk.CTkButton(
            input_frame, text="...", width=50, command=self.browse_btw_file
        )
        btw_browse_button.pack(side="right")
        # endregion

        # region PDF

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

        self.pdf_puth = CTk.CTkEntry(
            pdf_frame, placeholder_text="Путь к каталогу pdf", height=35
        )
        self.pdf_puth.pack(side="left", fill="x", expand=True, padx=(5, 10))
        self.pdf_browse_button = CTk.CTkButton(pdf_frame, text="...", width=50)
        self.pdf_browse_button.pack(side="right")
        # endregion

        # region JPG
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

        self.jpg_puth = CTk.CTkEntry(
            jpg_frame, placeholder_text="Путь к каталогу jpg", height=30
        )
        self.jpg_puth.pack(side="left", fill="x", expand=True, padx=(5, 10))
        self.jpg_browse_button = CTk.CTkButton(jpg_frame, text="...", width=50)
        self.jpg_browse_button.pack(side="right")
        # endregion

        # -------------------------------- Фрейм для ввода IP адреса ---------------------------
        # region Фрейм для поля ввода IP адреса

        CTk.CTkLabel(
            setting_frame,
            text="Настройки весов (IP адрес, определение стабильного веса, интервал опроса весов, порог нуля (г.), количество штук в пачке):",
            font=CTk.CTkFont(weight="bold"),
        ).pack(anchor="w", padx=10, pady=(20, 0))

        ip_frame = CTk.CTkFrame(setting_frame, fg_color="transparent")
        ip_frame.pack(fill="x", padx=10, pady=(5, 10))

        # Поле ввода для IP адреса с маской
        self.ip_address = CTk.CTkEntry(
            ip_frame,
            placeholder_text="Введите IP адрес",
            height=35,
        )
        self.ip_address.pack(side="left", fill="x", expand=True, padx=(0, 10))
        # endregion

        # region stability_threshold - Количество стабильных взвешиваний

        self.stability_threshold = CTk.CTkEntry(
            ip_frame,
            placeholder_text="Кол-во стаб.",
            height=35,
        )
        vcmd = (self.register(self.validate_numeric_input), "%P")
        self.stability_threshold.configure(validate="key", validatecommand=vcmd)
        self.stability_threshold.pack(side="left", fill="x", expand=True, padx=(0, 10))
        # endregion

        # region poll_interval - Интервал опроса весов

        self.poll_interval = CTk.CTkEntry(
            ip_frame,
            placeholder_text="Интервал опроса, с",
            height=35,
        )
        vcmd = (self.register(self.validate_float_input), "%P")
        self.poll_interval.configure(validate="key", validatecommand=vcmd)
        self.poll_interval.pack(side="left", fill="x", expand=True, padx=(0, 10))
        # endregion

        # region zero_threshold - Порог нуля
        self.zero_threshold = CTk.CTkEntry(
            ip_frame,
            placeholder_text="Порог нуля, г.",
            height=35,
        )
        vcmd = (self.register(self.validate_float_input), "%P")
        self.zero_threshold.configure(validate="key", validatecommand=vcmd)
        self.zero_threshold.pack(side="left", fill="x", expand=True, padx=(0, 10))
        # endregion

        # region Количество штук в пачке
        self.pieces_entry = CTk.CTkEntry(
            ip_frame,
            placeholder_text="Кол. штук в пачке",
            height=35,
        )
        vcmd = (self.register(self.validate_numeric_input), "%P")
        self.pieces_entry.configure(validate="key", validatecommand=vcmd)
        self.pieces_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        # endregion

        # region Фрейм для принтеров ---------------------------

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
            values=self.available_printers,  # Функция для определения списка доступных принтеров
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
        # endregion
