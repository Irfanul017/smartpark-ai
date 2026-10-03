"""Seed an idempotent SmartPark AI demo lot and local administrator."""

from __future__ import annotations

from app.database import SessionLocal, init_database
from app.models import ParkingSlot, User
from app.services.auth_service import auth_service


DEMO_SLOTS = (
    ("A01", "Car", False, False, False, 18, 22, 15),
    ("A02", "Car", False, False, True, 26, 32, 70),
    ("A03", "Car", False, False, False, 55, 42, 20),
    ("A04", "Electric Car", True, False, False, 35, 38, 10),
    ("A05", "Electric Car", True, False, False, 90, 78, 35),
    ("B01", "SUV", False, False, False, 65, 55, 15),
    ("B02", "SUV", False, False, True, 40, 44, 80),
    ("B03", "Van", False, False, False, 110, 95, 18),
    ("B04", "Car", False, True, False, 24, 20, 12),
    ("B05", "Car", False, True, False, 75, 65, 30),
    ("C01", "Bike", False, False, False, 12, 18, 8),
    ("C02", "Bike", False, False, False, 48, 40, 25),
    ("C03", "Bike", False, False, False, 75, 64, 35),
    ("C04", "Car", False, False, False, 105, 88, 25),
    ("C05", "Car", False, False, True, 130, 110, 70),
    ("D01", "Car", False, False, False, 42, 36, 18),
    ("D02", "Electric Car", True, False, False, 82, 70, 20),
    ("D03", "SUV", False, False, False, 115, 98, 40),
    ("D04", "Car", False, True, False, 58, 48, 15),
    ("D05", "Van", False, False, False, 150, 130, 45),
)


def seed_demo_data() -> tuple[int, bool]:
    """Create missing demo records without overwriting user-managed slot state."""
    init_database()
    database = SessionLocal()
    try:
        existing_numbers = {row[0] for row in database.query(ParkingSlot.slot_number).all()}
        for number, vehicle, is_ev, is_accessible, is_occupied, distance, walking, congestion in DEMO_SLOTS:
            if number in existing_numbers:
                continue
            database.add(ParkingSlot(
                slot_number=number,
                floor="G" if number[0] in {"A", "B"} else "1",
                zone=number[0],
                slot_type="Accessible" if is_accessible else "EV" if is_ev else "Normal",
                vehicle_type=vehicle,
                is_ev=is_ev,
                is_accessible=is_accessible,
                is_reserved=number == "D05",
                is_occupied=is_occupied,
                distance_from_entrance=distance,
                walking_distance=walking,
                congestion_level=congestion,
            ))
        admin_created = False
        if database.query(User).filter(User.username == "admin").first() is None:
            database.add(User(
                username="admin",
                email="admin@smartpark.local",
                password_hash=auth_service.hash_password("Admin@12345"),
                role="ADMIN",
            ))
            admin_created = True
        database.commit()
        return database.query(ParkingSlot).count(), admin_created
    finally:
        database.close()


if __name__ == "__main__":
    total_slots, admin_created = seed_demo_data()
    print(f"Demo data ready: {total_slots} slots; admin_created={admin_created}")
