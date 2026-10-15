import sys
import subprocess

print("=" * 60)
print(f"Поточний інтерпретатор Python:")
print(f"  {sys.executable}")
print(f"Версія Python: {sys.version}")
print("=" * 60)

packages = [
    ("fastapi", "fastapi"),
    ("uvicorn", "uvicorn"),
    ("sqlalchemy", "sqlalchemy"),
    ("pydantic", "pydantic"),
    ("jinja2", "jinja2"),
    ("pymysql", "pymysql"),
    ("cryptography", "cryptography"),
    ("dotenv", "python-dotenv"),
]

missing = []

for import_name, pkg_name in packages:
    try:
        __import__(import_name)
        print(f"  [OK] {pkg_name}")
    except ImportError:
        print(f"  [НЕ ЗНАЙДЕНО] {pkg_name}")
        missing.append(pkg_name)

print("=" * 60)

if missing:
    print(f"Відсутні пакети: {', '.join(missing)}")
    answer = input("Встановити їх прямо зараз для цього Python? (y/n): ").strip().lower()
    if answer in ["y", "yes", "д", "так", ""]:
        print("\nВстановлення...")
        cmd = [sys.executable, "-m", "pip", "install"] + missing
        res = subprocess.call(cmd)
        if res == 0:
            print("\nУсі відсутні пакети успішно встановлено!")
            print("Тепер імпорти працюватимуть.")
        else:
            print("\nПомилка встановлення через pip.")
else:
    print("Усі необхідні бібліотеки встановлені для цього Python!")

input("\nНатисніть Enter для виходу...")
