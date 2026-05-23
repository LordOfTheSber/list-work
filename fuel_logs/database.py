import os
import sqlite3
import atexit
from typing import Iterable

DB_PATH = os.path.join(os.path.dirname(__file__), "database.db")


class Database:
    def __init__(self, db_path: str = DB_PATH):
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.init_db()
        # Регистрируем автосохранение при завершении
        atexit.register(self.close)

    def init_db(self):
        cur = self.conn.cursor()
        cur.executescript(
            """
            PRAGMA foreign_keys = ON;
            CREATE TABLE IF NOT EXISTS drivers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL UNIQUE
            );

            CREATE TABLE IF NOT EXISTS vehicles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                brand TEXT NOT NULL,
                model TEXT NOT NULL,
                plate_number TEXT NOT NULL UNIQUE,
                fuel_norm_per_100km REAL NOT NULL,
                fuel_type TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS trip_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trip_number TEXT NOT NULL UNIQUE,
                start_date TEXT NOT NULL,
                end_date TEXT NOT NULL,
                driver_id INTEGER NOT NULL,
                vehicle_id INTEGER NOT NULL,
                odometer_start REAL NOT NULL,
                odometer_end REAL NOT NULL,
                fuel_start REAL NOT NULL,
                fuel_filled REAL NOT NULL,
                fuel_end REAL NOT NULL,
                FOREIGN KEY(driver_id) REFERENCES drivers(id) ON DELETE RESTRICT,
                FOREIGN KEY(vehicle_id) REFERENCES vehicles(id) ON DELETE RESTRICT
            );

            CREATE TABLE IF NOT EXISTS trip_photos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trip_id INTEGER NOT NULL,
                file_path TEXT NOT NULL,
                FOREIGN KEY(trip_id) REFERENCES trip_logs(id) ON DELETE CASCADE
            );
            """
        )
        self.conn.commit()

    def query(self, sql: str, params: Iterable = ()): 
        cur = self.conn.cursor()
        cur.execute(sql, params)
        self.conn.commit()
        return cur

    def fetchall(self, sql: str, params: Iterable = ()): 
        return self.query(sql, params).fetchall()

    def fetchone(self, sql: str, params: Iterable = ()): 
        return self.query(sql, params).fetchone()

    def close(self):
        if self.conn:
            self.conn.commit()  # Сохраняем все изменения
            self.conn.close()
