
from customtkinter import *
from PIL import Image

class App(CTk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        FRAME0 = CTkFrame(master=self, width=490, height=60)
        FRAME0.pack_propagate(False)
        FRAME0.pack(fill="both")
        self.LABEL1 = CTkLabel(master=FRAME0, text="Установки ", corner_radius=16, wraplength=0, height=13)
        self.LABEL1.pack()
        self.CHECKBOX3 = CTkCheckBox(master=FRAME0, text="", width=23)
        self.CHECKBOX3.pack(side="left")
        self.ENTRY4 = CTkEntry(master=FRAME0, placeholder_text="None")
        self.ENTRY4.pack(padx=(4, 4), expand=1, fill="x", side="left")
        BUTTON5 = CTkButton(master=FRAME0, text="Кнопка\n", fg_color=("#3B8ED0", "#3B8ED0"), width=141, image=CTkImage(Image.open(r"Assets\Screenshot_1.png"), size=(24, 24)))
        BUTTON5.pack(side="right")
        self.FRAME5 = CTkFrame(master=self)
        self.FRAME5.pack_propagate(False)
        self.FRAME5.pack(fill="x")
        self.BUTTON6 = CTkButton(master=self.FRAME5, text="Кнопка 2", font=CTkFont(family="Arial"))
        self.BUTTON6.pack()
        
set_default_color_theme("blue")
root = App()
root.geometry("500x500")
root.title("Window")
root.configure(fg_color=['gray92', 'gray14'])
root.mainloop()
            
