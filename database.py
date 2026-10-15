import os
import sys
import subprocess

# Автоматичне доустановлення pymysql та dotenv, якщо вони відсутні
try:
    import pymysql
except ImportError:
    print("[INFO] Бібліотека 'pymysql' не знайдена. Встановлення...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pymysql", "cryptography"])
    import pymysql

try:
    from dotenv import load_dotenv
except ImportError:
    print("[INFO] Бібліотека 'python-dotenv' не знайдена. Встановлення...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "python-dotenv"])
    from dotenv import load_dotenv

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Завантажуємо налаштування з файлу .env
load_dotenv()

MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
MYSQL_DB = os.getenv("MYSQL_DB", "ttn_database")


def ensure_database_exists():
    """Автоматично створює базу даних в MySQL, якщо вона ще не існує."""
    try:
        connection = pymysql.connect(
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            charset="utf8mb4",
        )
        with connection.cursor() as cursor:
            cursor.execute(
                f"CREATE DATABASE IF NOT EXISTS `{MYSQL_DB}` "
                f"CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
            )
        connection.commit()
        connection.close()
        print(f"[OK] База даних MySQL '{MYSQL_DB}' успішно підключена.")
    except Exception as e:
        print(f"\n[УВАГА] Не вдалося підключитися до сервера MySQL ({MYSQL_HOST}:{MYSQL_PORT}): {e}")
        print("Переконайтеся, що:")
        print(" 1. Сервер MySQL запущений (у службах Windows, XAMPP або OpenServer).")
        print(" 2. Параметри логіну/паролю у файлі .env вказані правильно.\n")


# Створюємо базу даних при старті
ensure_database_exists()

# URL для підключення через SQLAlchemy та драйвер PyMySQL
DATABASE_URL = (
    f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@"
    f"{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}?charset=utf8mb4"
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Перевіряє з'єднання перед виконанням запитів
    pool_recycle=3600,  # Оновлює з'єднання щогодини для запобігання тайм-ауту
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency для отримання сесії бази даних у FastAPI."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
