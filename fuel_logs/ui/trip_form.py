import os
import shutil
from datetime import datetime
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from PIL import Image, ImageTk

from .validators import parse_date_ru, parse_float_ru

ALLOWED_EXT = {".jpg", ".jpeg", ".png", ".pdf"}


class TripForm(ttk.Frame):
    def __init__(self, master, db, photos_dir):
        super().__init__(master)
        self.db = db
        self.photos_dir = photos_dir
        self.driver_map = {}
        self.vehicle_map = {}
        self.photo_paths = []
        self._build()
        self.refresh_lookups()
        self.load()

    def _build(self):
        f = ttk.LabelFrame(self, text="Новый путевой лист")
        f.pack(fill="x", padx=12, pady=12)
        self.fields = {}
        specs = [
            ("Номер", 0), ("Дата выезда", 1), ("Дата возврата", 2),
            ("Одометр нач.", 3), ("Одометр кон.", 4), ("Остаток нач.", 5),
            ("Заправлено", 6), ("Остаток кон.", 7),
        ]
        for txt, col in specs:
            ttk.Label(f, text=txt).grid(row=0, column=col, sticky="w")
            e = ttk.Entry(f, width=15)
            e.grid(row=1, column=col, padx=3, pady=3)
            self.fields[txt] = e

        ttk.Label(f, text="Водитель").grid(row=2, column=0, sticky="w")
        self.driver_cb = ttk.Combobox(f, state="readonly", width=25)
        self.driver_cb.grid(row=3, column=0, columnspan=2, sticky="w", padx=2)
        ttk.Label(f, text="Авто").grid(row=2, column=2, sticky="w")
        self.vehicle_cb = ttk.Combobox(f, state="readonly", width=25)
        self.vehicle_cb.grid(row=3, column=2, columnspan=2, sticky="w", padx=2)

        ttk.Button(f, text="Рассчитать", style="Accent.TButton", command=self.calculate).grid(row=3, column=4)
        ttk.Button(f, text="Добавить лист", style="Accent.TButton", command=self.add).grid(row=3, column=5)
        ttk.Button(f, text="Прикрепить фото", command=self.attach).grid(row=3, column=6)

        self.photos_lbl = ttk.Label(f, text="Файлы: 0")
        self.photos_lbl.grid(row=3, column=7, sticky="w")

        self.calc_lbl = ttk.Label(self, text="Пробег: -, Факт. расход: -, Норматив: -")
        self.calc_lbl.pack(anchor="w", padx=12)

        search = ttk.Frame(self)
        search.pack(fill="x", padx=12, pady=4)
        ttk.Label(search, text="Поиск").pack(side="left")
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self.load())
        ttk.Entry(search, textvariable=self.search_var, width=45).pack(side="left", padx=5)

        cols = ("id", "num", "dates", "driver", "vehicle", "odo", "fuel", "photos")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=12)
        names = ["ID", "Номер", "Период", "Водитель", "Гос.номер", "Пробег", "Факт. расход", "Файлов"]
        for c, n in zip(cols, names):
            self.tree.heading(c, text=n)
        self.tree.pack(fill="both", expand=True, padx=12, pady=8)

        btns = ttk.Frame(self)
        btns.pack(fill="x", padx=12, pady=5)
        ttk.Button(btns, text="Открыть последнее фото", command=self.open_photo).pack(side="left")
        ttk.Button(btns, text="Удалить лист", command=self.delete).pack(side="left", padx=5)

    def refresh_lookups(self):
        self.driver_map = {r["full_name"]: r["id"] for r in self.db.fetchall("SELECT id, full_name FROM drivers ORDER BY full_name")}
        self.driver_cb["values"] = list(self.driver_map.keys())
        self.vehicle_map = {r["plate_number"]: r["id"] for r in self.db.fetchall("SELECT id, plate_number FROM vehicles ORDER BY plate_number")}
        self.vehicle_cb["values"] = list(self.vehicle_map.keys())

    def _validated_trip_data(self):
        start = parse_date_ru(self.fields["Дата выезда"].get(), "Дата выезда")
        end = parse_date_ru(self.fields["Дата возврата"].get(), "Дата возврата")
        if end < start:
            raise ValueError("Дата возврата не может быть раньше даты выезда")
        odo_s = parse_float_ru(self.fields["Одометр нач."].get(), "Одометр нач.")
        odo_e = parse_float_ru(self.fields["Одометр кон."].get(), "Одометр кон.")
        if odo_e < odo_s:
            raise ValueError("Одометр конечный должен быть больше или равен начальному")
        fuel_s = parse_float_ru(self.fields["Остаток нач."].get(), "Остаток нач.")
        fuel_f = parse_float_ru(self.fields["Заправлено"].get(), "Заправлено")
        fuel_e = parse_float_ru(self.fields["Остаток кон."].get(), "Остаток кон.")
        if not self.driver_cb.get() or not self.vehicle_cb.get():
            raise ValueError("Выберите водителя и автомобиль")
        return start, end, odo_s, odo_e, fuel_s, fuel_f, fuel_e

    def calculate(self):
        try:
            _, _, odo_s, odo_e, fuel_s, fuel_f, fuel_e = self._validated_trip_data()
            mileage = odo_e - odo_s
            fact = fuel_s + fuel_f - fuel_e
            v = self.db.fetchone("SELECT fuel_norm_per_100km FROM vehicles WHERE id=?", (self.vehicle_map[self.vehicle_cb.get()],))
            norm = mileage * v["fuel_norm_per_100km"] / 100
            self.calc_lbl.config(text=f"Пробег: {mileage:.2f}, Факт. расход: {fact:.2f}, Норматив: {norm:.2f}")
            return mileage, fact, norm
        except Exception as e:
            messagebox.showerror("Ошибка валидации", str(e))

    def attach(self):
        paths = filedialog.askopenfilenames(filetypes=[("Files", "*.jpg *.jpeg *.png *.pdf")])
        added = 0
        for p in paths:
            if os.path.splitext(p.lower())[1] in ALLOWED_EXT and p not in self.photo_paths:
                self.photo_paths.append(p)
                added += 1
        self.photos_lbl.config(text=f"Файлы: {len(self.photo_paths)} (+{added})")

    def add(self):
        try:
            self.calculate()
            start, end, odo_s, odo_e, fuel_s, fuel_f, fuel_e = self._validated_trip_data()
            row_id = self.db.query(
                """INSERT INTO trip_logs(trip_number,start_date,end_date,driver_id,vehicle_id,odometer_start,odometer_end,fuel_start,fuel_filled,fuel_end)
                VALUES(?,?,?,?,?,?,?,?,?,?)""",
                (self.fields["Номер"].get().strip(), start, end, self.driver_map[self.driver_cb.get()], self.vehicle_map[self.vehicle_cb.get()], odo_s, odo_e, fuel_s, fuel_f, fuel_e),
            ).lastrowid
            for source in self.photo_paths:
                name = f"trip_{row_id}_{datetime.now().strftime('%Y%m%d%H%M%S%f')}_{os.path.basename(source)}"
                target = os.path.join(self.photos_dir, name)
                shutil.copy2(source, target)
                self.db.query("INSERT INTO trip_photos(trip_id,file_path) VALUES(?,?)", (row_id, target))
            self.photo_paths.clear()
            self.photos_lbl.config(text="Файлы: 0")
            self.load()
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def load(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        q = self.search_var.get().strip()
        rows = self.db.fetchall("""
            SELECT t.*, d.full_name, v.plate_number,
                   (t.odometer_end - t.odometer_start) as mileage,
                   (t.fuel_start + t.fuel_filled - t.fuel_end) as fact,
                   (SELECT COUNT(1) FROM trip_photos p WHERE p.trip_id=t.id) as photos_count
            FROM trip_logs t
            JOIN drivers d ON d.id=t.driver_id
            JOIN vehicles v ON v.id=t.vehicle_id
            WHERE (?='' OR t.trip_number LIKE '%'||?||'%' OR d.full_name LIKE '%'||?||'%' OR v.plate_number LIKE '%'||?||'%')
            ORDER BY t.start_date DESC
        """, (q, q, q, q))
        for r in rows:
            self.tree.insert("", "end", values=(r["id"], r["trip_number"], f"{r['start_date']} - {r['end_date']}", r["full_name"], r["plate_number"], round(r["mileage"], 2), round(r["fact"], 2), r["photos_count"]))

    def delete(self):
        sel = self.tree.selection()
        if not sel: return
        self.db.query("DELETE FROM trip_logs WHERE id=?", (self.tree.item(sel[0])["values"][0],))
        self.load()

    def open_photo(self):
        sel = self.tree.selection()
        if not sel: return
        trip_id = self.tree.item(sel[0])["values"][0]
        row = self.db.fetchone("SELECT file_path FROM trip_photos WHERE trip_id=? ORDER BY id DESC LIMIT 1", (trip_id,))
        if not row:
            messagebox.showinfo("Фото", "Нет прикрепленных файлов")
            return
        path = row["file_path"]
        if path.lower().endswith(".pdf"):
            messagebox.showinfo("PDF", f"PDF-файл: {path}")
            return
        win = tk.Toplevel(self)
        win.title("Фото путевого листа")
        image = Image.open(path)
        image.thumbnail((1200, 900))
        photo = ImageTk.PhotoImage(image)
        lbl = ttk.Label(win, image=photo)
        lbl.image = photo
        lbl.pack()
