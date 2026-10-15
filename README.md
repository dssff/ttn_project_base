# Система бази даних MySQL та REST API

Програма на Python з базою даних **MySQL**, візуальним веб-інтерфейсом для введення даних та повнофункціональним REST API для передачі та отримання даних.

---

## ⚙️ Налаштування підключення до MySQL

Параметри підключення зберігаються у файлі [`.env`](file:///d:/ttn_developer/.env):
```env
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=
MYSQL_DB=ttn_database
```
*Якщо пароль порожній (наприклад, у XAMPP / OpenServer), залиште `MYSQL_PASSWORD=` без значення.*  
*База даних `ttn_database` та всі 6 таблиць створюються в MySQL автоматично при першому запуску!*

---

## 📋 Структура таблиць бази даних

1. **`kontragents`**: `id`, `medcode`, `name`, `full_name`, `ipn`, `endpou`, `ur_fiz`
2. **`data_info`**: `id`, `object`, `type`, `k`, `v`
3. **`people`**: `id`, `code`, `name`, `full_name`
4. **`place`**: `id`, `name`, `owner`, `area`, `crop`, `people`
5. **`technika`**: `id`, `avtomobil`, `misce_ystanovky`, `derj_nomer`, `vin`, `d`, `w`, `rik`, `v`, `ekipaj`, `telefony`, `pricep`, `kontragent`, `model`, `kolir`, `telegram`, `medcode`, `wialon_id`, `dodatkovo`
6. **`dop_data_technika`**: `id`, `ts`, `rik`, `vin`, `d`, `w`, `v`, `misce_zberiganny`

---

## 🚀 Встановлення та запуск

### 1. Встановіть необхідні бібліотеки:
```bash
pip install -r requirements.txt
```

### 2. Запустіть сервер:
```bash
python main.py
```
*або через uvicorn:*
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

---

## 🖥️ Візуальний інтерфейс користувача

Відкрийте у будь-якому браузері:
👉 **[http://127.0.0.1:8000](http://127.0.0.1:8000)**

**Можливості інтерфейсу:**
- Перемикання між усіма 6 таблицями в один клік.
- Додавання нових записів через зручне модальне вікно.
- Редагування та видалення існуючих записів.
- Миттєвий пошук та фільтрація записів у реальному часі.
- Лічильники кількості записів у кожній таблиці.
- Кнопка експорту всієї бази даних у JSON.

---

## 📡 REST API (Передача та отримання даних)

### 📖 Інтерактивна документація (Swagger UI):
Відкрийте **[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)** для тестування будь-яких API-запитів безпосередньо у браузері.

### Ендпоінти для кожної таблиці:

| Таблиця | Отримати всі (GET) | Отримати один (GET) | Створити (POST) | Оновити (PUT) | Видалити (DELETE) |
|---|---|---|---|---|---|
| **kontragents** | `/api/kontragents/` | `/api/kontragents/{id}` | `/api/kontragents/` | `/api/kontragents/{id}` | `/api/kontragents/{id}` |
| **data_info** | `/api/data_info/` | `/api/data_info/{id}` | `/api/data_info/` | `/api/data_info/{id}` | `/api/data_info/{id}` |
| **people** | `/api/people/` | `/api/people/{id}` | `/api/people/` | `/api/people/{id}` | `/api/people/{id}` |
| **place** | `/api/place/` | `/api/place/{id}` | `/api/place/` | `/api/place/{id}` | `/api/place/{id}` |
| **technika** | `/api/technika/` | `/api/technika/{id}` | `/api/technika/` | `/api/technika/{id}` | `/api/technika/{id}` |
| **dop_data_technika** | `/api/dop_data_technika/` | `/api/dop_data_technika/{id}` | `/api/dop_data_technika/` | `/api/dop_data_technika/{id}` | `/api/dop_data_technika/{id}` |

### Додаткові корисні ендпоінти:
- **`GET /api/export/all`** — повертає повний JSON дамп усіх таблиць одразу.

### Приклади запитів:

#### 1. Отримати список техніки через Python (`requests`):
```python
import requests

response = requests.get("http://127.0.0.1:8000/api/technika/")
data = response.json()
print(data)
```

#### 2. Додати нового контрагента через cURL:
```bash
curl -X POST "http://127.0.0.1:8000/api/kontragents/" \
  -H "Content-Type: application/json" \
  -d '{
    "medcode": "MED-2001",
    "name": "Новий Контрагент",
    "full_name": "ТОВ Новий Контрагент",
    "ipn": "123456789012",
    "endpou": "12345678",
    "ur_fiz": "Юридична особа"
  }'
```
