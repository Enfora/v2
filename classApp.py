import customtkinter as CTk
import win32print
import tkinter.filedialog as filedialog
import tkinter.messagebox as messagebox
import os
import json
import sys

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

        # Проверяем доступность win32print в конструкторе
        self.WIN32PRINT_AVAILABLE = self.check_win32print_availability()
        self.available_printers = self.get_available_printers()

        self.Init_Interface_Settings()  # Отрисовка страницы настроек

        if self.WIN32PRINT_AVAILABLE:
            print("⚠ Получение списка принтеров доступно")

        self.load_settings()

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
        self.browse_directory(self.pdf_puth)

    def browse_directory_jpg(self):
        self.jpg_browse_button._state = "disabled"
        self.browse_directory(self.jpg_puth)

    def browse_directory(self, entry_widget):
        """Открыть диалог выбора директории"""
        directory = filedialog.askdirectory(title="Выберите папку")
        if directory:
            entry_widget.delete(0, "end")
            entry_widget.insert(0, directory)

    # ФУНКЦИИ СОХРАНЕНИЯ НАСТРОЕК
    def save_settings(self):  # Запоминаем настройки в JSON
        """Сохранение настроек в JSON файл"""
        settings = {
            "checkbox_jpg": bool(self.checkbox_jpg.get()),
            "checkbox_pdf": bool(self.checkbox_pdf.get()),
            "jpg_entry": self.jpg_puth.get(),
            "pdf_entry": self.pdf_puth.get(),
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

            self.pdf_puth.delete(0, "end")
            self.pdf_puth.insert(0, settings.get("pdf_entry", ""))

            self.jpg_puth.delete(0, "end")
            self.jpg_puth.insert(0, settings.get("jpg_entry", ""))

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
            #messagebox.showerror("Error", error_msg)
            print(f"✗ {error_msg}")

    # endregion

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

    def Init_Interface_Settings(self):

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

        self.pdf_puth = CTk.CTkEntry(
            pdf_frame, placeholder_text="Путь к каталогу pdf", height=35
        )
        self.pdf_puth.pack(side="left", fill="x", expand=True, padx=(5, 10))
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

        self.jpg_puth = CTk.CTkEntry(
            jpg_frame, placeholder_text="Путь к каталогу jpg", height=30
        )
        self.jpg_puth.pack(side="left", fill="x", expand=True, padx=(5, 10))
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

        # ОТРИСОВКА РАБОЧЕЙ ОБЛАСТИ

        # Кнопки вверху слева
        button_frame = CTk.CTkFrame(tab_workarea, fg_color="transparent", height=40)
        button_frame.pack(side="top", anchor="nw", fill="x", pady=(0, 10), padx=10)

        self.action_button = CTk.CTkButton(
            button_frame,
            text="Инициализация BarTender",
            width=120,
            height=35,
            font=CTk.CTkFont(size=12, weight="bold"),
            command=self.initialize_bar_tender,
        )
        self.action_button.pack(side="left", padx=(0, 10))
