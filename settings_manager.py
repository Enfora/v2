import json
import os
import tkinter.messagebox as messagebox


# ФУНКЦИИ СОХРАНЕНИЯ НАСТРОЕК
def save_settings_manager(self):  # Запоминаем настройки в JSON
    settings_data = {
        "checkbox_pdf": bool(self.checkbox_pdf.get()),
        "pdf_entry": self.pdf_path.get(),
        "template_entry": self.template_entry.get(),
        "template_entry_total": self.template_entry_total.get(),
        "ip_address": self.ip_address.get(),
        "pieces_entry": self.pieces_entry.get(),
        "unit_printer": self.unit_printer_combo.get(),
        "total_printer": self.total_printer_combo.get(),
        "stability_threshold": self.stability_threshold.get(),
        "poll_interval": self.poll_interval.get(),
        "zero_threshold": self.zero_threshold.get(),
    }

    """Сохранение настроек в JSON файл"""
    try:
        with open("settings.json", "w", encoding="utf-8") as f:
            json.dump(settings_data, f, ensure_ascii=False, indent=2)
        # messagebox.showinfo("Успех", "Настройки успешно сохранены в settings.json")
        print("✓ Настройки успешно сохранены в settings.json")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось сохранить настройки: {e}")
        print(f"✗ Ошибка сохранения настроек: {e}")


def load_settings_manager(self):
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
            #     Заполняем поля ввода
            self.template_entry.delete(0, "end")
            self.template_entry.insert(0, settings.get("template_entry", ""))

            #     Заполняем поля ввода
            self.template_entry_total.delete(0, "end")
            self.template_entry_total.insert(0, settings.get("template_entry_total", ""))

            self.pdf_path.delete(0, "end")
            self.pdf_path.insert(0, settings.get("pdf_entry", ""))

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

            # messagebox.showinfo("Успех", "Настройки успешно загружены")

        print("✓ Настройки успешно загружены из settings.json")

        return settings

    except json.JSONDecodeError:
        messagebox.showerror(
            "Ошибка", "Файл настроек поврежден или имеет неверный формат."
        )
        print("✗ Ошибка: Файл настроек поврежден или имеет неверный формат.")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось загрузить настройки: {e}")
        print(f"✗ Ошибка загрузки настроек: {e}")
        return {}
