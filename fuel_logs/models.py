from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class Driver:
    id: Optional[int]
    full_name: str


@dataclass
class Vehicle:
    id: Optional[int]
    brand: str
    model: str
    plate_number: str
    fuel_norm_per_100km: float
    fuel_type: str


@dataclass
class TripLog:
    id: Optional[int]
    trip_number: str
    start_date: date
    end_date: date
    driver_id: int
    vehicle_id: int
    odometer_start: float
    odometer_end: float
    fuel_start: float
    fuel_filled: float
    fuel_end: float
