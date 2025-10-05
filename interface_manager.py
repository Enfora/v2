import customtkinter as CTk
import tkinter.filedialog as filedialog
import tkinter.messagebox as messagebox


def Init_Interface_Settings_manager(self):

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
        tab_console = tabview.add("Консоль")

        self.create_console_frame(tab_console)

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
            command=self.save_settings,
        )
        save_button.pack(side="left", padx=(0, 10))

        load_button = CTk.CTkButton(  # Кнопка Загрузить настройки
            frameButtons,
            text="Загрузить настройки",
            width=120,
            command=self.load_settings,
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
            input_frame,
            text="...",
            width=50,
            hover=True,
            hover_color="blue",
            command=self.browse_btw_file,
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

        self.pdf_path = CTk.CTkEntry(
            pdf_frame, placeholder_text="Путь к каталогу pdf", height=35
        )
        self.pdf_path.pack(side="left", fill="x", expand=True, padx=(5, 10))
        self.pdf_browse_button = CTk.CTkButton(
            pdf_frame,
            text="...",
            width=50,
            hover_color="blue",
            hover=True,
            command=self.browse_directory_pdf,
        )
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

        self.jpg_path = CTk.CTkEntry(
            jpg_frame, placeholder_text="Путь к каталогу jpg", height=30
        )
        self.jpg_path.pack(side="left", fill="x", expand=True, padx=(5, 10))
        self.jpg_browse_button = CTk.CTkButton(
            jpg_frame,
            text="...",
            width=50,
            hover=True,
            hover_color="blue",
            command=self.browse_directory_jpg,
        )
        self.jpg_browse_button.pack(side="right")
        # endregion

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
            placeholder_text="Порог нуля, кг.",
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

        # ОТРИСОВКА РАБОЧЕЙ ОБЛАСТИ

        # Кнопки вверху слева
        button_frame = CTk.CTkFrame(tab_workarea, fg_color="transparent", height=40)
        button_frame.pack(side="top", anchor="nw", fill="x", pady=(0, 10), padx=10)

        init_button_bartender = CTk.CTkButton(
            button_frame,
            text="Инициализация BarTender",
            width=120,
            height=35,
            font=CTk.CTkFont(size=12, weight="bold"),
            command=self.initialize_bar_tender
        )
        init_button_bartender.pack(side="left", padx=(0, 10))

        # Кнопка начать взвешивание
        start_button = CTk.CTkButton(
            button_frame,
            text="Начать",
            width=120,
            height=35,
            font=CTk.CTkFont(size=12, weight="bold"),
            command=self.getWeightThreading_Enable
        )
        start_button.pack(side="left", padx=(0, 10))

        # Кнопка остановить взвешивание
        stop_button = CTk.CTkButton(
            button_frame,
            text="Остановить",
            width=120,
            height=35,
            font=CTk.CTkFont(size=12, weight="bold"),
            command=self.getWeightThreading_Disable
        )
        stop_button.pack(side="left", padx=(0, 10))

        # Кнопка очистки таблицы
        clear_button_table = CTk.CTkButton(
            button_frame,
            text="Очистка таблицы",
            width=120,
            height=35,
            font=CTk.CTkFont(size=12, weight="bold"),
            command=self.clear_table
        )
        clear_button_table.pack(side="left", padx=(0, 10))

        # Фрейм для вывода текущего веса
        current_weight_frame = CTk.CTkFrame(
            tab_workarea, height=150, fg_color="black", corner_radius=10
        )
        current_weight_frame.pack(side="top", fill="x", padx=5, pady=5)

        # Поле для отображения веса
        self.current_weight = CTk.CTkLabel(
            current_weight_frame,
            text="0.000",
            font=CTk.CTkFont(family="Digital-7 Mono", size=200),
            text_color="#00FF00",
            fg_color="black",
            bg_color="black",
        )
        self.current_weight.pack(expand=True, fill="both", padx=20, pady=20)

        # Информация с историей веса и этикеткой
        table_frame = CTk.CTkFrame(tab_workarea)
        table_frame.pack(side="top", fill="both", expand=True, padx=10, pady=10)
        
        # Заголовок таблицы
        CTk.CTkLabel(
            table_frame,
            text="ИСТОРИЯ ВЗВЕШИВАНИЙ",
            font=CTk.CTkFont(size=14, weight="bold"),
        ).pack(pady=(5, 5))

        info_frame = CTk.CTkFrame(table_frame, bg_color="red")
        info_frame.pack(side="top", fill="both", expand=True, padx=10, pady=10)

        # Создаем таблицу (Treeview)
        self.weights_table = CTk.CTkTextbox(
            info_frame,
            height=200,
            font=CTk.CTkFont(
                family="Consolas", size=14
            ),  # Моноширинный шрифт для таблицы
        )
        self.weights_table.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        # Фрейм для фото (чтобы лучше контролировать отступы)
        photo_frame = CTk.CTkFrame(info_frame)
        photo_frame.pack(side="right", fill="both", expand=True, padx=(5, 5), pady=5)

        self.photo = CTk.CTkLabel(photo_frame, text="", fg_color="transparent")
        self.photo.pack(side="right", fill="both", expand=True, padx=5, pady=5)

        # Добавляем заголовки колонок
        header = "ВРЕМЯ                  ВЕС (кг)\n"
        header += "─────────────────────────────────\n"
        self.weights_table.insert("1.0", header)
        self.weights_table.configure(state="disabled")  # Делаем только для чтения