import customtkinter as CTk


class App(CTk.CTk):
    def __init__(self):
        super().__init__()
        self.Init_Interface()

    # region Вспомогательные ФУНКЦИИ
    def validate_numeric_input(self, new_text):
        """Функция проверяет что ввод содержит только цифры"""
        return new_text.isdigit() or new_text == ""

    def validate_float_input(self, new_text):
        """Проверяет ввод чисел с плавающей точкой"""
        if new_text == "" or new_text == "-":
            return True
        try:
            float(new_text)
            return True
        except ValueError:
            return False

    # endregion

    def Init_Interface(self):

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
        btw_browse_button = CTk.CTkButton(input_frame, text="...", width=50)
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

        CTk.CTkLabel(
            setting_frame,
            text="Настройки весов (IP адрес, определение стабильного веса, интервал опроса весов, порог нуля (г.), количество штук в пачке):",
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

        # region stability_threshold - Количество стабильных взвешиваний
        vcmd = (self.register(self.validate_numeric_input), "%P")
        self.stability_threshold = CTk.CTkEntry(
            ip_frame,
            validate="key",
            validatecommand=vcmd,
            placeholder_text="Кол-во взвешиваний для опред. стабильности",
            height=35,
        )
        self.stability_threshold.pack(side="left", fill="x", expand=True, padx=(0, 10))
        # endregion

        # region Поле для ввода poll_interval - Интервал опроса весов
        vcmd = (self.register(self.validate_float_input), "%P")
        self.poll_interval = CTk.CTkEntry(
            ip_frame,
            validate="key",
            validatecommand=vcmd,
            placeholder_text="Интервал опроса весов, с",
            height=35,
        )
        self.poll_interval.pack(side="left", fill="x", expand=True, padx=(0, 10))
        # endregion

        # region Поле для ввода zero_threshold - Порог нуля
        vcmd = (self.register(self.validate_numeric_input), "%P")
        self.zero_threshold = CTk.CTkEntry(
            ip_frame,
            validate="key",
            validatecommand=vcmd,
            placeholder_text="Порог нуля, г.",
            height=35,
        )
        self.zero_threshold.pack(side="left", fill="x", expand=True, padx=(0, 10))
        # endregion

        # Поле ввода для количества штук в пачке
        vcmd = (self.register(self.validate_numeric_input), "%P")
        self.pieces_entry = CTk.CTkEntry(
            ip_frame,
            validate="key",
            validatecommand=vcmd,
            placeholder_text="Введите количество штук в пачке (например: 12)...",
            height=35,
        )
        self.pieces_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        # endregion

    # endregion

    # Сначала регистрируем функцию валидации
    # self.vcmd = (self.register(self.validate_numeric_input), "%P")
