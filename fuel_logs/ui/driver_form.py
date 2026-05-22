from tkinter import ttk, messagebox


class DriverForm(ttk.Frame):
    def __init__(self, master, db, refresh_callbacks=()):
        super().__init__(master)
        self.db = db
        self.refresh_callbacks = refresh_callbacks
        self._build()
        self.load()

    def _build(self):
        top = ttk.Frame(self)
        top.pack(fill="x", padx=8, pady=8)
        ttk.Label(top, text="ФИО:").pack(side="left")
        self.full_name = ttk.Entry(top, width=45)
        self.full_name.pack(side="left", padx=5)
        ttk.Button(top, text="Добавить", command=self.add).pack(side="left", padx=5)
        ttk.Button(top, text="Удалить выбранного", command=self.delete).pack(side="left", padx=5)

        self.tree = ttk.Treeview(self, columns=("id", "full_name"), show="headings", height=12)
        self.tree.heading("id", text="ID")
        self.tree.heading("full_name", text="ФИО")
        self.tree.pack(fill="both", expand=True, padx=8, pady=8)

    def load(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        for row in self.db.fetchall("SELECT id, full_name FROM drivers ORDER BY full_name"):
            self.tree.insert("", "end", values=(row["id"], row["full_name"]))

    def add(self):
        name = self.full_name.get().strip()
        if not name:
            return
        try:
            self.db.query("INSERT INTO drivers(full_name) VALUES (?)", (name,))
            self.full_name.delete(0, "end")
            self.load()
            self._notify()
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def delete(self):
        sel = self.tree.selection()
        if not sel:
            return
        driver_id = self.tree.item(sel[0])["values"][0]
        try:
            self.db.query("DELETE FROM drivers WHERE id=?", (driver_id,))
            self.load()
            self._notify()
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def _notify(self):
        for cb in self.refresh_callbacks:
            cb()
