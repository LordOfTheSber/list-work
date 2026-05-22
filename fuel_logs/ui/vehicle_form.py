from tkinter import ttk, messagebox

from .validators import validate_plate, parse_float_ru


class VehicleForm(ttk.Frame):
    def __init__(self, master, db, refresh_callbacks=()):
        super().__init__(master)
        self.db = db
        self.refresh_callbacks = refresh_callbacks
        self._build()
        self.load()

    def _build(self):
        form = ttk.LabelFrame(self, text="Карточка ТС")
        form.pack(fill="x", padx=8, pady=8)
        labels = ["Марка", "Модель", "Гос. номер", "Норма (л/100км)", "Тип топлива"]
        self.entries = {}
        for i, text in enumerate(labels):
            ttk.Label(form, text=text).grid(row=0, column=i)
            e = ttk.Entry(form, width=16)
            e.grid(row=1, column=i, padx=3)
            self.entries[text] = e
        ttk.Button(form, text="Добавить", command=self.add).grid(row=1, column=len(labels), padx=5)
        ttk.Button(form, text="Удалить", command=self.delete).grid(row=1, column=len(labels)+1, padx=5)

        self.tree = ttk.Treeview(self, columns=("id", "brand", "model", "plate", "norm", "fuel_type", "mileage", "fuel_balance"), show="headings", height=12)
        for c, t in [("id", "ID"), ("brand", "Марка"), ("model", "Модель"), ("plate", "Гос.номер"), ("norm", "Норма"), ("fuel_type", "Топливо"), ("mileage", "Общий пробег"), ("fuel_balance", "Остаток топлива")]:
            self.tree.heading(c, text=t)
        self.tree.pack(fill="both", expand=True, padx=8, pady=8)

    def load(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        rows = self.db.fetchall(
            """
            SELECT v.*, COALESCE(MAX(t.odometer_end),0) as mileage,
                   COALESCE((SELECT fuel_end FROM trip_logs tl WHERE tl.vehicle_id=v.id ORDER BY end_date DESC LIMIT 1),0) as fuel_balance
            FROM vehicles v
            LEFT JOIN trip_logs t ON t.vehicle_id=v.id
            GROUP BY v.id
            ORDER BY v.plate_number
            """
        )
        for row in rows:
            self.tree.insert("", "end", values=(row["id"], row["brand"], row["model"], row["plate_number"], row["fuel_norm_per_100km"], row["fuel_type"], round(row["mileage"], 2), round(row["fuel_balance"], 2)))

    def add(self):
        try:
            self.db.query(
                "INSERT INTO vehicles(brand, model, plate_number, fuel_norm_per_100km, fuel_type) VALUES (?,?,?,?,?)",
                (
                    self.entries["Марка"].get().strip(),
                    self.entries["Модель"].get().strip(),
                    validate_plate(self.entries["Гос. номер"].get()),
                    parse_float_ru(self.entries["Норма (л/100км)"].get(), "Норма (л/100км)", min_value=0.1),
                    self.entries["Тип топлива"].get().strip(),
                ),
            )
            for e in self.entries.values():
                e.delete(0, "end")
            self.load()
            self._notify()
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def delete(self):
        sel = self.tree.selection()
        if not sel:
            return
        vehicle_id = self.tree.item(sel[0])["values"][0]
        try:
            self.db.query("DELETE FROM vehicles WHERE id=?", (vehicle_id,))
            self.load()
            self._notify()
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def _notify(self):
        for cb in self.refresh_callbacks:
            cb()
