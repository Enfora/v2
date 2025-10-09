import customtkinter as ctk
from tkcalendar import Calendar
from datetime import datetime

class CalendarApp:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Календарь")
        
        # Поле для отображения выбранной даты
        self.date_entry = ctk.CTkEntry(self.root, width=120, placeholder_text="дд.мм.гггг")
        self.date_entry.pack(pady=10)
        
        # Кнопка для открытия календаря
        self.calendar_btn = ctk.CTkButton(
            self.root, 
            text="📅 Выбрать дату", 
            command=self.open_calendar
        )
        self.calendar_btn.pack(pady=10)
        
        # Всплывающее окно для календаря
        self.calendar_window = None
    
    def open_calendar(self):
        """Открывает окно с календарем"""
        if self.calendar_window is None or not self.calendar_window.winfo_exists():
            # Создаем Toplevel окно (из tkinter)
            self.calendar_window = ctk.CTkToplevel(self.root)
            self.calendar_window.title("Выберите дату")
            self.calendar_window.geometry("400x400")
            self.calendar_window.transient(self.root)  # Поведение модального окна
            self.calendar_window.grab_set()  # Захватываем фокус
            
            # Создаем календарь (из tkcalendar)
            calendar = Calendar(
                self.calendar_window, 
                selectmode='day',
                year=datetime.now().year,
                month=datetime.now().month,
                day=datetime.now().day,
                date_pattern='dd.mm.yyyy'
            )
            calendar.pack(pady=20, padx=20, fill="both", expand=True)
            
            # Кнопка подтверждения выбора
            select_btn = ctk.CTkButton(
                self.calendar_window,
                text="Выбрать",
                command=lambda: self.select_date(calendar)
            )
            select_btn.pack(pady=10)
            
            # Кнопка отмены
            cancel_btn = ctk.CTkButton(
                self.calendar_window,
                text="Отмена",
                command=self.calendar_window.destroy,
                fg_color="transparent",
                border_width=1
            )
            cancel_btn.pack(pady=5)
        else:
            self.calendar_window.lift()  # Поднимаем окно поверх других
    
    def select_date(self, calendar):
        """Обрабатывает выбор даты из календаря"""
        selected_date = calendar.get_date()
        self.date_entry.delete(0, "end")
        self.date_entry.insert(0, selected_date)
        self.calendar_window.destroy()
        self.calendar_window = None
    
    def run(self):
        self.root.mainloop()

# Установите tkcalendar: pip install tkcalendar
app = CalendarApp()
app.run()