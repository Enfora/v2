import customtkinter as CTk


def Init_Interface(self):
    # Окно и заголовок программы
    self.geometry("1024x768")
    self.resizable = (False, False)  # type: ignore
    self.title("Оболочка для сетевых весов. Enfora@2025")

    # Создаем вкладки TabView
    tabview = CTk.CTkTabview(self)
    tabview.pack(padx=10, pady=10, fill="both", expand=True)

    """Создание вкладок"""
    tab_workarea = tabview.add("Рабочая область")
    tab_settings = tabview.add("Настройки")

    # Формирование Настроек
    # Заголовок
    CTk.CTkLabel(
        tab_settings,
        text="Общие настройки весов и шаблонов", 
        font=CTk.CTkFont(size=16, weight="bold"),
    ).pack(pady=10)

    # Фрейм для кнопок чтения и сохранения настроек
    # Фрейм для кнопок сохранения/загрузки вверху слева
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

    # Фрейм для области настроек
    setting_frame = CTk.CTkFrame(tab_settings, fg_color="lightgrey")
    setting_frame.pack(side="top", fill="both", expand=True, pady=5, padx=10)

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
    btw_browse_button = CTk.CTkButton(input_frame, text="Обзор...", width=100)
    btw_browse_button.pack(side="right")

    # PDF
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
        pdf_frame, placeholder_text="Путь к каталогу pdf", height=35
    )
    self.pdf_entry.pack(side="left", fill="x", expand=True, padx=(5, 10))
    self.pdf_browse_button = CTk.CTkButton(pdf_frame, text="Обзор...", width=100)
    self.pdf_browse_button.pack(side="right")

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
        jpg_frame, placeholder_text="Путь к каталогу jpg", height=35
    )
    self.jpg_entry.pack(side="left", fill="x", expand=True, padx=(5, 10))
    self.jpg_browse_button = CTk.CTkButton(jpg_frame, text="Обзор...", width=100)
    self.jpg_browse_button.pack(side="right")


class App(CTk.CTk):
    def __init__(self):
        super().__init__()
        Init_Interface(self)
