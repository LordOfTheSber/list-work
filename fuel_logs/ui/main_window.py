import tkinter as tk
from tkinter import ttk

from .driver_form import DriverForm
from .vehicle_form import VehicleForm
from .trip_form import TripForm
from .calculator import CalculatorFrame


class MainWindow(tk.Tk):
    def __init__(self, db, photos_dir):
        super().__init__()
        self.title("Учёт путевых листов")
        self.geometry("1400x900")

        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True)

        self.trip_form = TripForm(nb, db, photos_dir)
        vehicle_form = VehicleForm(nb, db, refresh_callbacks=(self.trip_form.refresh_lookups,))
        driver_form = DriverForm(nb, db, refresh_callbacks=(self.trip_form.refresh_lookups,))
        report_frame = self._build_report_tab(nb, db)
        calc_frame = CalculatorFrame(nb)

        nb.add(self.trip_form, text="Путевые листы")
        nb.add(vehicle_form, text="Автопарк")
        nb.add(driver_form, text="Водители")
        nb.add(report_frame, text="Аналитика")
        nb.add(calc_frame, text="Калькулятор")

    def _build_report_tab(self, master, db):
        frame = ttk.Frame(master)
        top = ttk.Frame(frame)
        top.pack(fill="x", padx=8, pady=8)
        ttk.Label(top, text="Период с (YYYY-MM-DD)").pack(side="left")
        start = ttk.Entry(top, width=15)
        start.pack(side="left", padx=3)
        ttk.Label(top, text="по").pack(side="left")
        end = ttk.Entry(top, width=15)
        end.pack(side="left", padx=3)

        tree = ttk.Treeview(frame, columns=("plate", "fuel"), show="headings")
        tree.heading("plate", text="Гос. номер")
        tree.heading("fuel", text="Суммарный расход")
        tree.pack(fill="both", expand=True, padx=8, pady=8)

        def run_report():
            for i in tree.get_children():
                tree.delete(i)
            rows = db.fetchall(
                """
                SELECT v.plate_number, SUM(t.fuel_start+t.fuel_filled-t.fuel_end) as fuel_total
                FROM trip_logs t JOIN vehicles v ON v.id=t.vehicle_id
                WHERE t.start_date>=? AND t.end_date<=?
                GROUP BY v.plate_number
                ORDER BY v.plate_number
                """,
                (start.get().strip(), end.get().strip()),
            )
            for r in rows:
                tree.insert("", "end", values=(r["plate_number"], round(r["fuel_total"] or 0, 2)))

        ttk.Button(top, text="Построить", command=run_report).pack(side="left", padx=8)
        return frame
