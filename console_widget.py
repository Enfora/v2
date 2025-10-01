import customtkinter as ctk
import sys


class SimpleConsole(ctk.CTkTextbox):
    """
    Кастомная консоль для вывода текста
    Наследуется от CTkTextbox и перенаправляет stdout
    """
    
    def __init__(self, master, **kwargs):
        # Устанавливаем значения по умолчанию
        kwargs.setdefault('fg_color', 'black')
        kwargs.setdefault('text_color', 'white')
        kwargs.setdefault('font', ('Consolas', 11))
        kwargs.setdefault('wrap', 'word')
        
        super().__init__(master, **kwargs)
        
        # Сохраняем оригинальный stdout и перенаправляем вывод
        self.old_stdout = sys.stdout
        sys.stdout = self
        
        # Делаем консоль только для чтения
        self.configure(state='normal')
    
    def write(self, text):
        """Перехватывает вывод из print() и добавляет в текстовое поле"""
        self.insert("end", text)
        self.see("end")
        self.update_idletasks()  # Обновляем интерфейс
    
    def flush(self):
        """Требуется для совместимости с sys.stdout"""
        pass
    
    def clear(self):
        """Очищает консоль"""
        self.delete("1.0", "end")
    
    def destroy(self):
        """Восстанавливает оригинальный stdout при уничтожении"""
        sys.stdout = self.old_stdout
        super().destroy()