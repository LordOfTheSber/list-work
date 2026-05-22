import os

from database import Database
from ui.main_window import MainWindow


def main():
    base_dir = os.path.dirname(__file__)
    photos_dir = os.path.join(base_dir, "photos")
    os.makedirs(photos_dir, exist_ok=True)

    db = Database()
    app = MainWindow(db, photos_dir)
    app.mainloop()
    db.close()


if __name__ == "__main__":
    main()
