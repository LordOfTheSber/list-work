import tkinter as tk
from tkinter import ttk, messagebox


class CalculatorFrame(ttk.LabelFrame):
    def __init__(self, master):
        super().__init__(master, text="Калькулятор")
        self.expr = tk.StringVar()
        ttk.Entry(self, textvariable=self.expr).grid(row=0, column=0, columnspan=4, sticky="ew", padx=5, pady=5)
        buttons = [
            "7", "8", "9", "/",
            "4", "5", "6", "*",
            "1", "2", "3", "-",
            "0", ".", "=", "+",
        ]
        for idx, b in enumerate(buttons):
            r, c = divmod(idx, 4)
            ttk.Button(self, text=b, command=lambda x=b: self.on_click(x), width=6).grid(row=r+1, column=c, padx=3, pady=3)
        ttk.Button(self, text="C", command=lambda: self.expr.set("")).grid(row=5, column=0, columnspan=4, sticky="ew", padx=3, pady=3)

    def on_click(self, value: str):
        if value == "=":
            try:
                self.expr.set(str(eval(self.expr.get(), {"__builtins__": {}}, {})))
            except Exception:
                messagebox.showerror("Ошибка", "Некорректное выражение")
        else:
            self.expr.set(self.expr.get() + value)
