import socket
import sys

print("=" * 60)
print("Діагностика порту та запуску...")
print("=" * 60)

# 1. Перевірка зайнятості порту 8000
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
result = sock.connect_ex(('127.0.0.1', 8000))
sock.close()

if result == 0:
    print("[+] Порт 8000 вже відкритий і слухає з'єднання!")
    print("    Спробуйте оновити сторінку у браузері: http://127.0.0.1:8000")
else:
    print("[-] Порт 8000 зараз закритий (сервер не запущений або зупинився).")
    print("    Зараз спробуємо запустити main.py і подивитися на помилки, якщо вони є...\n")

    try:
        import main
        print("[+] Модуль main.py успішно імпортувався без помилок!")
        print("    Запускаємо uvicorn...\n")
        import uvicorn
        uvicorn.run(main.app, host="127.0.0.1", port=8000)
    except Exception as e:
        print(f"\n[ПОМИЛКА при запуску]: {e}")
        import traceback
        traceback.print_exc()

input("\nНатисніть Enter...")
