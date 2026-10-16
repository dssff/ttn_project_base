import sys
import subprocess

# Автоматичне встановлення відсутніх залежностей при запуску
REQUIRED_PACKAGES = [
    ("fastapi", "fastapi"),
    ("uvicorn", "uvicorn"),
    ("sqlalchemy", "sqlalchemy"),
    ("pydantic", "pydantic"),
    ("jinja2", "jinja2"),
    ("pymysql", "pymysql"),
    ("cryptography", "cryptography"),
    ("dotenv", "python-dotenv"),
]

for import_name, pkg_name in REQUIRED_PACKAGES:
    try:
        __import__(import_name)
    except ImportError:
        print(f"[INFO] Бібліотека '{pkg_name}' не знайдена. Встановлення...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg_name])

from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
import os

from database import engine, Base, get_db
import models
import schemas

# Create database tables if they do not exist yet
try:
    Base.metadata.create_all(bind=engine)
    print("[OK] Таблиці MySQL перевірено / створено успішно.")
except Exception as e:
    print(f"\n[ПОМИЛКА] Не вдалося створити таблиці в базі даних: {e}")
    print("Перевірте права користувача MySQL або налаштування у файлі .env\n")

app = FastAPI(
    title="Data & Logistics API",
    description="REST API та система візуального управління базою даних MySQL",
    version="1.0.0",
)

# Enable CORS for cross-origin integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==========================================
# Seeding initial demonstration data
# ==========================================
def seed_demo_data():
    try:
        db = next(get_db())
        if db.query(models.Kontragent).count() == 0:
            db.add(
                models.Kontragent(
                    medcode="MED-1001",
                    name="Агро-Трейд",
                    full_name='ТОВ "Агро-Трейд Компані"',
                    ipn="384729105123",
                    endpou="38472910",
                    ur_fiz="Юридична особа",
                )
            )
            db.add(
                models.Kontragent(
                    medcode="MED-1002",
                    name="Петренко І.В.",
                    full_name="ФОП Петренко Ігор Васильович",
                    ipn="2918273645",
                    endpou="2918273645",
                    ur_fiz="Фізична особа",
                )
            )

        if db.query(models.DataInfo).count() == 0:
            # Детальна інформація по контрагентах в data_info
            db.add(
                models.DataInfo(
                    object="Агро-Трейд",
                    type="kontragent",
                    k="Юридична адреса",
                    v="м. Київ, вул. Хрещатик, 1, оф. 10",
                )
            )
            db.add(
                models.DataInfo(
                    object="Агро-Трейд",
                    type="kontragent",
                    k="Телефон",
                    v="+380441234567",
                )
            )
            db.add(
                models.DataInfo(
                    object="Агро-Трейд",
                    type="kontragent",
                    k="Факс",
                    v="+380441234568",
                )
            )
            db.add(
                models.DataInfo(
                    object="Петренко І.В.",
                    type="kontragent",
                    k="Юридична адреса",
                    v="м. Полтава, вул. Соборності, 25",
                )
            )
            db.add(
                models.DataInfo(
                    object="Петренко І.В.",
                    type="kontragent",
                    k="Телефон",
                    v="+380509876543",
                )
            )
            db.add(
                models.DataInfo(
                    object="GPS_Sensor_A1",
                    type="Telemetry",
                    k="calibration_status",
                    v="active",
                )
            )
            db.add(
                models.DataInfo(
                    object="Fuel_Tank_01",
                    type="Capacity",
                    k="max_volume_liters",
                    v="600",
                )
            )

        if db.query(models.Person).count() == 0:
            db.add(
                models.Person(
                    code="EMP-01",
                    name="Іван",
                    full_name="Шевченко Іван Олексійович",
                )
            )
            db.add(
                models.Person(
                    code="EMP-02",
                    name="Олександр",
                    full_name="Коваль Олександр Миколайович",
                )
            )

        if db.query(models.Nomenklatyra).count() == 0:
            db.add(
                models.Nomenklatyra(
                    code="NOM-101",
                    name="Пшениця озима 2 клас",
                    type="Зернові",
                    od_vym="т",
                    vpv_1_3="Зерно пшениці насипом, вологість 13.5%",
                    dodatkovo="ДСТУ 3768:2019",
                )
            )
            db.add(
                models.Nomenklatyra(
                    code="NOM-102",
                    name="Кукурудза",
                    type="Зернові",
                    od_vym="т",
                    vpv_1_3="Зерно кукурудзи насипом",
                    dodatkovo="3 клас",
                )
            )
            db.add(
                models.Nomenklatyra(
                    code="NOM-103",
                    name="Соняшник",
                    type="Олійні",
                    od_vym="т",
                    vpv_1_3="Насіння соняшнику олійне",
                    dodatkovo="Олійність 48%",
                )
            )
            db.add(
                models.Nomenklatyra(
                    code="NOM-104",
                    name="Ріпак",
                    type="Олійні",
                    od_vym="т",
                    vpv_1_3="Насіння ріпаку ярого",
                    dodatkovo="Кондиційний",
                )
            )

        if db.query(models.Place).count() == 0:
            db.add(
                models.Place(
                    name="Східне Поле №12",
                    owner="Агро-Трейд",
                    area="145.8 га",
                    crop="Пшениця озима 2 клас",
                    people="Шевченко Іван Олексійович",
                )
            )

        if db.query(models.Technika).count() == 0:
            db.add(
                models.Technika(
                    avtomobil="AX1234CA",
                    misce_ystanovky="Гараж №1",
                    derj_nomer="AX1234CA",
                    vin="WMA06XZZ8LP987654",
                    d="12.5",
                    w="2.5",
                    rik="2021",
                    v="85",
                    ekipaj="Шевченко Іван Олексійович",
                    telefony="+380501112233",
                    pricep="Напівпричіп KRONE",
                    kontragent="Агро-Трейд",
                    model="MAN TGX 18.440",
                    kolir="Синій",
                    telegram="@driver_ivan",
                    medcode="MED-1001",
                    wialon_id="99812",
                    dodatkovo="Встановлено новий GPS-трекер та датчик рівня палива",
                )
            )

        if db.query(models.DopDataTechnika).count() == 0:
            db.add(
                models.DopDataTechnika(
                    ts="AX1234CA",
                    rik="2021",
                    vin="WMA06XZZ8LP987654",
                    d="12.5",
                    w="2.5",
                    v="85",
                    misce_zberiganny="Центральний автопарк (Сектор В)",
                )
            )

        db.commit()
        db.close()
    except Exception as e:
        print(f"[INFO] Початкова ініціалізація даних пропущена: {e}")


seed_demo_data()


# ==========================================
# Visual UI Route
# ==========================================
@app.get("/", response_class=HTMLResponse, tags=["Visual Interface"])
def read_root():
    """Повертає головну веб-сторінку з інтерфейсом для внесення та перегляду даних."""
    template_path = os.path.join(
        os.path.dirname(__file__), "templates", "index.html"
    )
    if os.path.exists(template_path):
        with open(template_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(
        content="<h3>Шаблон templates/index.html не знайдено</h3>",
        status_code=404,
    )


# ==========================================
# 1. API: Kontragents (зв'язані з data_info)
# ==========================================
def enrich_kontragent(item: models.Kontragent, db: Session) -> schemas.KontragentResponse:
    """Підтягує детальні параметри (адреса, телефон, факс) з таблиці data_info."""
    details = {"ur_address": None, "phone": None, "fax": None}
    names_to_check = [name.strip() for name in [item.name, item.full_name, f"Контрагент #{item.id}"] if name and name.strip()]
    if names_to_check:
        info_rows = (
            db.query(models.DataInfo)
            .filter(models.DataInfo.object.in_(names_to_check))
            .all()
        )
        for r in info_rows:
            k_lower = (r.k or "").strip().lower()
            if any(term in k_lower for term in ["адрес", "address", "юр"]):
                details["ur_address"] = r.v
            elif any(term in k_lower for term in ["телефон", "phone", "тел"]):
                details["phone"] = r.v
            elif any(term in k_lower for term in ["факс", "fax"]):
                details["fax"] = r.v

    return schemas.KontragentResponse(
        id=item.id,
        medcode=item.medcode,
        name=item.name,
        full_name=item.full_name,
        ipn=item.ipn,
        endpou=item.endpou,
        ur_fiz=item.ur_fiz,
        ur_address=details["ur_address"],
        phone=details["phone"],
        fax=details["fax"],
    )


@app.get(
    "/api/kontragents/",
    response_model=List[schemas.KontragentResponse],
    tags=["1. Kontragents"],
)
def get_kontragents(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(models.Kontragent)
    if search:
        query = query.filter(
            (models.Kontragent.name.ilike(f"%{search}%"))
            | (models.Kontragent.full_name.ilike(f"%{search}%"))
            | (models.Kontragent.ipn.ilike(f"%{search}%"))
            | (models.Kontragent.endpou.ilike(f"%{search}%"))
        )
    items = query.offset(skip).limit(limit).all()
    return [enrich_kontragent(item, db) for item in items]


@app.get(
    "/api/kontragents/{item_id}",
    response_model=schemas.KontragentResponse,
    tags=["1. Kontragents"],
)
def get_kontragent(item_id: int, db: Session = Depends(get_db)):
    item = (
        db.query(models.Kontragent)
        .filter(models.Kontragent.id == item_id)
        .first()
    )
    if not item:
        raise HTTPException(
            status_code=404, detail="Контрагента з таким ID не знайдено"
        )
    return enrich_kontragent(item, db)


@app.post(
    "/api/kontragents/",
    response_model=schemas.KontragentResponse,
    status_code=201,
    tags=["1. Kontragents"],
)
def create_kontragent(
    data: schemas.KontragentCreate, db: Session = Depends(get_db)
):
    data_dict = data.model_dump()
    ur_address = data_dict.pop("ur_address", None)
    phone = data_dict.pop("phone", None)
    fax = data_dict.pop("fax", None)

    # 1. Створюємо запис у таблиці kontragents
    item = models.Kontragent(**data_dict)
    db.add(item)
    db.commit()
    db.refresh(item)

    # 2. Визначаємо назву об'єкта для data_info (name або full_name)
    obj_name = item.name or item.full_name or f"Контрагент #{item.id}"

    # 3. Автоматично вносимо параметри в таблицю data_info
    if ur_address and ur_address.strip():
        db.add(
            models.DataInfo(
                object=obj_name,
                type="kontragent",
                k="Юридична адреса",
                v=ur_address.strip(),
            )
        )
    if phone and phone.strip():
        db.add(
            models.DataInfo(
                object=obj_name,
                type="kontragent",
                k="Телефон",
                v=phone.strip(),
            )
        )
    if fax and fax.strip():
        db.add(
            models.DataInfo(
                object=obj_name,
                type="kontragent",
                k="Факс",
                v=fax.strip(),
            )
        )

    db.commit()
    return enrich_kontragent(item, db)


@app.put(
    "/api/kontragents/{item_id}",
    response_model=schemas.KontragentResponse,
    tags=["1. Kontragents"],
)
def update_kontragent(
    item_id: int, data: schemas.KontragentUpdate, db: Session = Depends(get_db)
):
    item = (
        db.query(models.Kontragent)
        .filter(models.Kontragent.id == item_id)
        .first()
    )
    if not item:
        raise HTTPException(
            status_code=404, detail="Контрагента з таким ID не знайдено"
        )

    data_dict = data.model_dump()
    ur_address = data_dict.pop("ur_address", None)
    phone = data_dict.pop("phone", None)
    fax = data_dict.pop("fax", None)

    old_names = [n for n in [item.name, item.full_name] if n]

    # Оновлюємо поля контрагента
    for key, value in data_dict.items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)

    new_obj_name = item.name or item.full_name or f"Контрагент #{item.id}"

    # Якщо ім'я контрагента змінилося — синхронізуємо поле object у data_info, technika.kontragent та place.owner
    if old_names and old_names[0] != new_obj_name:
        db.query(models.DataInfo).filter(
            models.DataInfo.object.in_(old_names)
        ).update({"object": new_obj_name}, synchronize_session=False)

        # Синхронізуємо перевізника в картках техніки (tehnika ⟷ kontragents)
        db.query(models.Technika).filter(
            models.Technika.kontragent.in_(old_names)
        ).update({"kontragent": item.name}, synchronize_session=False)

        # Синхронізуємо власника точок завантаження (place ⟷ kontragents)
        db.query(models.Place).filter(
            models.Place.owner.in_(old_names)
        ).update({"owner": item.name}, synchronize_session=False)

    # Оновлюємо / додаємо / видаляємо записи в data_info для кожного параметра
    param_map = [
        (["Юридична адреса", "Юридический адрес", "Юр. адреса", "ur_address", "Адреса", "Адрес"], ur_address, "Юридична адреса"),
        (["Телефон", "phone", "Телефон контрагента", "Тел."], phone, "Телефон"),
        (["Факс", "fax", "Факс контрагента"], fax, "Факс"),
    ]

    for k_variants, val, default_k in param_map:
        clean_val = val.strip() if val is not None else ""
        existing = (
            db.query(models.DataInfo)
            .filter(
                models.DataInfo.object == new_obj_name,
                models.DataInfo.k.in_(k_variants),
            )
            .all()
        )

        if not clean_val:
            # Значення було прибране/стерте в формі -> видаляємо відповідний запис з data_info
            for row in existing:
                db.delete(row)
        else:
            # Значення вказане -> оновлюємо існуючий запис або додаємо новий
            if existing:
                existing[0].v = clean_val
                # Видаляємо дублікати, якщо такі були
                for dup in existing[1:]:
                    db.delete(dup)
            else:
                db.add(
                    models.DataInfo(
                        object=new_obj_name,
                        type="kontragent",
                        k=default_k,
                        v=clean_val,
                    )
                )

    db.commit()
    return enrich_kontragent(item, db)


@app.delete("/api/kontragents/{item_id}", tags=["1. Kontragents"])
def delete_kontragent(item_id: int, db: Session = Depends(get_db)):
    item = (
        db.query(models.Kontragent)
        .filter(models.Kontragent.id == item_id)
        .first()
    )
    if not item:
        raise HTTPException(
            status_code=404, detail="Контрагента з таким ID не знайдено"
        )

    # Знаходимо всі варіанти назв контрагента для очищення data_info, technika та place
    names = [n.strip() for n in [item.name, item.full_name, f"Контрагент #{item.id}"] if n and n.strip()]

    # Спочатку видаляємо всі пов'язані записи з таблиці data_info
    if names:
        db.query(models.DataInfo).filter(
            models.DataInfo.object.in_(names)
        ).delete(synchronize_session=False)

        # Очищаємо зв'язки у technika (перевізник) та place (власник)
        db.query(models.Technika).filter(
            models.Technika.kontragent.in_(names)
        ).update({"kontragent": None}, synchronize_session=False)

        db.query(models.Place).filter(
            models.Place.owner.in_(names)
        ).update({"owner": None}, synchronize_session=False)

    # Видаляємо сам запис контрагента
    db.delete(item)
    db.commit()
    return {
        "status": "success",
        "message": f"Контрагента #{item_id} та пов'язані дані в data_info/техніці видалено",
    }


# ==========================================
# 2. API: Data Info
# ==========================================
@app.get(
    "/api/data_info/",
    response_model=List[schemas.DataInfoResponse],
    tags=["2. Data Info"],
)
def get_data_info_list(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(models.DataInfo)
    if search:
        query = query.filter(
            (models.DataInfo.object.ilike(f"%{search}%"))
            | (models.DataInfo.type.ilike(f"%{search}%"))
            | (models.DataInfo.k.ilike(f"%{search}%"))
        )
    return query.offset(skip).limit(limit).all()


@app.get(
    "/api/data_info/{item_id}",
    response_model=schemas.DataInfoResponse,
    tags=["2. Data Info"],
)
def get_data_info_item(item_id: int, db: Session = Depends(get_db)):
    item = (
        db.query(models.DataInfo).filter(models.DataInfo.id == item_id).first()
    )
    if not item:
        raise HTTPException(
            status_code=404, detail="Запис data_info не знайдено"
        )
    return item


@app.post(
    "/api/data_info/",
    response_model=schemas.DataInfoResponse,
    status_code=201,
    tags=["2. Data Info"],
)
def create_data_info(
    data: schemas.DataInfoCreate, db: Session = Depends(get_db)
):
    item = models.DataInfo(**data.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@app.put(
    "/api/data_info/{item_id}",
    response_model=schemas.DataInfoResponse,
    tags=["2. Data Info"],
)
def update_data_info(
    item_id: int, data: schemas.DataInfoUpdate, db: Session = Depends(get_db)
):
    item = (
        db.query(models.DataInfo).filter(models.DataInfo.id == item_id).first()
    )
    if not item:
        raise HTTPException(
            status_code=404, detail="Запис data_info не знайдено"
        )
    for key, value in data.model_dump().items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return item


@app.delete("/api/data_info/{item_id}", tags=["2. Data Info"])
def delete_data_info(item_id: int, db: Session = Depends(get_db)):
    item = (
        db.query(models.DataInfo).filter(models.DataInfo.id == item_id).first()
    )
    if not item:
        raise HTTPException(
            status_code=404, detail="Запис data_info не знайдено"
        )
    db.delete(item)
    db.commit()
    return {"status": "success", "message": f"Запис data_info #{item_id} видалено"}


# ==========================================
# 3. API: People
# ==========================================
@app.get(
    "/api/people/",
    response_model=List[schemas.PersonResponse],
    tags=["3. People"],
)
def get_people(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(models.Person)
    if search:
        query = query.filter(
            (models.Person.name.ilike(f"%{search}%"))
            | (models.Person.full_name.ilike(f"%{search}%"))
            | (models.Person.code.ilike(f"%{search}%"))
        )
    return query.offset(skip).limit(limit).all()


@app.get(
    "/api/people/{item_id}",
    response_model=schemas.PersonResponse,
    tags=["3. People"],
)
def get_person(item_id: int, db: Session = Depends(get_db)):
    item = db.query(models.Person).filter(models.Person.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Запис особи не знайдено")
    return item


@app.post(
    "/api/people/",
    response_model=schemas.PersonResponse,
    status_code=201,
    tags=["3. People"],
)
def create_person(data: schemas.PersonCreate, db: Session = Depends(get_db)):
    item = models.Person(**data.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@app.put(
    "/api/people/{item_id}",
    response_model=schemas.PersonResponse,
    tags=["3. People"],
)
def update_person(
    item_id: int, data: schemas.PersonUpdate, db: Session = Depends(get_db)
):
    item = db.query(models.Person).filter(models.Person.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Запис особи не знайдено")

    old_names = [n.strip() for n in [item.name, item.full_name] if n and n.strip()]

    for key, value in data.model_dump().items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)

    new_driver_name = item.full_name or item.name
    # Якщо ім'я водія змінилося — оновлюємо technika.ekipaj та place.people
    if old_names and new_driver_name:
        db.query(models.Technika).filter(
            models.Technika.ekipaj.in_(old_names)
        ).update({"ekipaj": new_driver_name}, synchronize_session=False)

        db.query(models.Place).filter(
            models.Place.people.in_(old_names)
        ).update({"people": new_driver_name}, synchronize_session=False)
        db.commit()

    return item


@app.delete("/api/people/{item_id}", tags=["3. People"])
def delete_person(item_id: int, db: Session = Depends(get_db)):
    item = db.query(models.Person).filter(models.Person.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Запис особи не знайдено")

    names = [n.strip() for n in [item.name, item.full_name] if n and n.strip()]

    # Очищаємо посилання на водія в technika та place
    if names:
        db.query(models.Technika).filter(
            models.Technika.ekipaj.in_(names)
        ).update({"ekipaj": None}, synchronize_session=False)

        db.query(models.Place).filter(
            models.Place.people.in_(names)
        ).update({"people": None}, synchronize_session=False)

    db.delete(item)
    db.commit()
    return {"status": "success", "message": f"Особу #{item_id} та посилання в техніці/місцях видалено"}


# ==========================================
# Вспоміжні сервісні функції зв'язків між таблицями
# ==========================================
def get_data_by_ts(ts: Optional[str], db: Session) -> Optional[dict]:
    """1. tehnika ⟷ dop_data_tehnika: підтягує технічні параметри (габарити, рік, vin) за держномером/ТЗ."""
    if not ts or not ts.strip():
        return None
    cleaned = ts.strip()
    dop = (
        db.query(models.DopDataTechnika)
        .filter(
            (models.DopDataTechnika.ts == cleaned)
            | (models.DopDataTechnika.vin == cleaned)
        )
        .first()
    )
    if not dop:
        dop = (
            db.query(models.DopDataTechnika)
            .filter(
                (models.DopDataTechnika.ts.ilike(f"%{cleaned}%"))
                | (models.DopDataTechnika.vin.ilike(f"%{cleaned}%"))
            )
            .first()
        )
    return dop.to_dict() if dop else None


def getvodiy(ekipaj: Optional[str], db: Session) -> Optional[dict]:
    """3. tehnika ⟷ people: знаходить повний запис водія/співробітника в таблиці people."""
    if not ekipaj or not ekipaj.strip():
        return None
    cleaned = ekipaj.strip()
    person = (
        db.query(models.Person)
        .filter(
            (models.Person.name == cleaned)
            | (models.Person.full_name == cleaned)
            | (models.Person.code == cleaned)
        )
        .first()
    )
    if not person:
        person = (
            db.query(models.Person)
            .filter(
                (models.Person.full_name.ilike(f"%{cleaned}%"))
                | (models.Person.name.ilike(f"%{cleaned}%"))
            )
            .first()
        )
    return person.to_dict() if person else None


def get_kontragent_info(kontragent_name: Optional[str], db: Session) -> Optional[dict]:
    """2. tehnika ⟷ kontragents: підтягує повні реквізити контрагента-перевізника та його адресу з data_info."""
    if not kontragent_name or not kontragent_name.strip():
        return None
    cleaned = kontragent_name.strip()
    k_obj = (
        db.query(models.Kontragent)
        .filter(
            (models.Kontragent.name == cleaned)
            | (models.Kontragent.full_name == cleaned)
        )
        .first()
    )
    if not k_obj:
        k_obj = (
            db.query(models.Kontragent)
            .filter(
                (models.Kontragent.name.ilike(f"%{cleaned}%"))
                | (models.Kontragent.full_name.ilike(f"%{cleaned}%"))
            )
            .first()
        )
    if not k_obj:
        return None

    res = k_obj.to_dict()
    # Підтягуємо юридичну адресу та контакти з data_info
    names = [n for n in [k_obj.name, k_obj.full_name] if n]
    infos = db.query(models.DataInfo).filter(models.DataInfo.object.in_(names)).all()
    for inf in infos:
        k_low = (inf.k or "").lower()
        if any(term in k_low for term in ["адрес", "address", "юр"]):
            res["ur_address"] = inf.v
        elif any(term in k_low for term in ["телефон", "phone", "тел"]):
            res["phone"] = inf.v
        elif any(term in k_low for term in ["факс", "fax"]):
            res["fax"] = inf.v
    return res


def get_nomenklatyra_info(crop_name: Optional[str], db: Session) -> Optional[dict]:
    """5. place ⟷ nomenklatyra: підтягує культуру та її характеристики для ТТН (vpv_1_3)."""
    if not crop_name or not crop_name.strip():
        return None
    cleaned = crop_name.strip()
    nom = (
        db.query(models.Nomenklatyra)
        .filter(
            (models.Nomenklatyra.name == cleaned)
            | (models.Nomenklatyra.code == cleaned)
        )
        .first()
    )
    if not nom:
        nom = (
            db.query(models.Nomenklatyra)
            .filter(models.Nomenklatyra.name.ilike(f"%{cleaned}%"))
            .first()
        )
    return nom.to_dict() if nom else None


def enrich_place(item: models.Place, db: Session) -> schemas.PlaceResponse:
    """Збагачує пункт завантаження відповідальною особою (people) та культурою (nomenklatyra)."""
    people_info = getvodiy(item.people, db)
    crop_info = get_nomenklatyra_info(item.crop, db)
    return schemas.PlaceResponse(
        id=item.id,
        name=item.name,
        owner=item.owner,
        area=item.area,
        crop=item.crop,
        people=item.people,
        people_info=people_info,
        crop_info=crop_info,
    )


def enrich_technika(item: models.Technika, db: Session) -> schemas.TechnikaResponse:
    """Збагачує техніку габаритами з dop_data_technika, перевізником з kontragents та водієм з people."""
    ts_key = item.avtomobil or item.derj_nomer
    dop = get_data_by_ts(ts_key, db)
    kontr = get_kontragent_info(item.kontragent, db)
    vodiy = getvodiy(item.ekipaj, db)

    # Якщо габарити або рік відсутні безпосередньо в картці — підставляємо з dop_data_technika
    d_val = item.d or (dop.get("d") if dop else None)
    w_val = item.w or (dop.get("w") if dop else None)
    v_val = item.v or (dop.get("v") if dop else None)
    rik_val = item.rik or (dop.get("rik") if dop else None)
    vin_val = item.vin or (dop.get("vin") if dop else None)
    misce_val = dop.get("misce_zberiganny") if dop else None

    return schemas.TechnikaResponse(
        id=item.id,
        avtomobil=item.avtomobil,
        misce_ystanovky=item.misce_ystanovky,
        derj_nomer=item.derj_nomer,
        vin=vin_val,
        d=d_val,
        w=w_val,
        rik=rik_val,
        v=v_val,
        ekipaj=item.ekipaj,
        telefony=item.telefony,
        pricep=item.pricep,
        kontragent=item.kontragent,
        model=item.model,
        kolir=item.kolir,
        telegram=item.telegram,
        medcode=item.medcode,
        wialon_id=item.wialon_id,
        dodatkovo=item.dodatkovo,
        misce_zberiganny=misce_val,
        dop_data=dop,
        kontragent_info=kontr,
        vodiy_info=vodiy,
    )


# ==========================================
# 4. API: Place (Точки завантаження/розвантаження)
# ==========================================
@app.get(
    "/api/place/",
    response_model=List[schemas.PlaceResponse],
    tags=["4. Place"],
)
def get_places(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(models.Place)
    if search:
        query = query.filter(
            (models.Place.name.ilike(f"%{search}%"))
            | (models.Place.owner.ilike(f"%{search}%"))
            | (models.Place.crop.ilike(f"%{search}%"))
            | (models.Place.people.ilike(f"%{search}%"))
        )
    items = query.offset(skip).limit(limit).all()
    return [enrich_place(p, db) for p in items]


@app.get(
    "/api/place/{item_id}",
    response_model=schemas.PlaceResponse,
    tags=["4. Place"],
)
def get_place(item_id: int, db: Session = Depends(get_db)):
    item = db.query(models.Place).filter(models.Place.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Місце / поле не знайдено")
    return enrich_place(item, db)


@app.post(
    "/api/place/",
    response_model=schemas.PlaceResponse,
    status_code=201,
    tags=["4. Place"],
)
def create_place(data: schemas.PlaceCreate, db: Session = Depends(get_db)):
    item = models.Place(**data.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return enrich_place(item, db)


@app.put(
    "/api/place/{item_id}",
    response_model=schemas.PlaceResponse,
    tags=["4. Place"],
)
def update_place(
    item_id: int, data: schemas.PlaceUpdate, db: Session = Depends(get_db)
):
    item = db.query(models.Place).filter(models.Place.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Місце / поле не знайдено")
    for key, value in data.model_dump().items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return enrich_place(item, db)


@app.delete("/api/place/{item_id}", tags=["4. Place"])
def delete_place(item_id: int, db: Session = Depends(get_db)):
    item = db.query(models.Place).filter(models.Place.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Місце / поле не знайдено")
    db.delete(item)
    db.commit()
    return {"status": "success", "message": f"Місце #{item_id} видалено"}


# ==========================================
# 5. API: Technika (Транспорт зі зв'язками)
# ==========================================
@app.get(
    "/api/technika/",
    response_model=List[schemas.TechnikaResponse],
    tags=["5. Technika"],
)
def get_technika_list(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(models.Technika)
    if search:
        query = query.filter(
            (models.Technika.avtomobil.ilike(f"%{search}%"))
            | (models.Technika.derj_nomer.ilike(f"%{search}%"))
            | (models.Technika.vin.ilike(f"%{search}%"))
            | (models.Technika.model.ilike(f"%{search}%"))
            | (models.Technika.kontragent.ilike(f"%{search}%"))
            | (models.Technika.ekipaj.ilike(f"%{search}%"))
        )
    items = query.offset(skip).limit(limit).all()
    return [enrich_technika(item, db) for item in items]


@app.get(
    "/api/technika/{item_id}",
    response_model=schemas.TechnikaResponse,
    tags=["5. Technika"],
)
def get_technika_item(item_id: int, db: Session = Depends(get_db)):
    item = (
        db.query(models.Technika).filter(models.Technika.id == item_id).first()
    )
    if not item:
        raise HTTPException(status_code=404, detail="Техніку не знайдено")
    return enrich_technika(item, db)


def validate_technika_linked_fields(data_dict: dict, db: Session):
    """Перевіряє, що контрагент та екіпаж/водій існують у базі даних (суворий вибір)."""
    kontragent = data_dict.get("kontragent")
    if kontragent and str(kontragent).strip():
        k_clean = str(kontragent).strip()
        k_found = db.query(models.Kontragent).filter(
            (models.Kontragent.name == k_clean)
            | (models.Kontragent.full_name == k_clean)
        ).first()
        if not k_found:
            k_found = db.query(models.Kontragent).filter(
                (models.Kontragent.name.ilike(k_clean))
                | (models.Kontragent.full_name.ilike(k_clean))
            ).first()
        if not k_found:
            raise HTTPException(
                status_code=400,
                detail=f"Контрагента '{k_clean}' не знайдено в базі даних. Оберіть контрагента з існуючих у базі."
            )
        data_dict["kontragent"] = k_found.name

    ekipaj = data_dict.get("ekipaj")
    if ekipaj and str(ekipaj).strip():
        e_clean = str(ekipaj).strip()
        p_found = db.query(models.Person).filter(
            (models.Person.full_name == e_clean)
            | (models.Person.name == e_clean)
            | (models.Person.code == e_clean)
        ).first()
        if not p_found:
            p_found = db.query(models.Person).filter(
                (models.Person.full_name.ilike(e_clean))
                | (models.Person.name.ilike(e_clean))
            ).first()
        if not p_found:
            raise HTTPException(
                status_code=400,
                detail=f"Водія/екіпаж '{e_clean}' не знайдено в базі даних. Оберіть особу з існуючих у базі."
            )
        data_dict["ekipaj"] = p_found.full_name or p_found.name


@app.post(
    "/api/technika/",
    response_model=schemas.TechnikaResponse,
    status_code=201,
    tags=["5. Technika"],
)
def create_technika(
    data: schemas.TechnikaCreate, db: Session = Depends(get_db)
):
    data_dict = data.model_dump()
    misce_zberiganny = data_dict.pop("misce_zberiganny", None)

    # Перевіряємо, що контрагент та екіпаж існують в базі даних
    validate_technika_linked_fields(data_dict, db)

    item = models.Technika(**data_dict)
    db.add(item)
    db.commit()
    db.refresh(item)

    # 1. Автоматично синхронізуємо запис у dop_data_technika
    ts_key = (item.avtomobil or item.derj_nomer or "").strip()
    if ts_key:
        existing_dop = (
            db.query(models.DopDataTechnika)
            .filter(models.DopDataTechnika.ts == ts_key)
            .first()
        )
        if existing_dop:
            if item.d: existing_dop.d = item.d
            if item.w: existing_dop.w = item.w
            if item.v: existing_dop.v = item.v
            if item.rik: existing_dop.rik = item.rik
            if item.vin: existing_dop.vin = item.vin
            if misce_zberiganny: existing_dop.misce_zberiganny = misce_zberiganny
        else:
            if any([item.d, item.w, item.v, item.rik, item.vin, misce_zberiganny]):
                db.add(
                    models.DopDataTechnika(
                        ts=ts_key,
                        rik=item.rik,
                        vin=item.vin,
                        d=item.d,
                        w=item.w,
                        v=item.v,
                        misce_zberiganny=misce_zberiganny,
                    )
                )
        db.commit()

    return enrich_technika(item, db)


@app.put(
    "/api/technika/{item_id}",
    response_model=schemas.TechnikaResponse,
    tags=["5. Technika"],
)
def update_technika(
    item_id: int, data: schemas.TechnikaUpdate, db: Session = Depends(get_db)
):
    item = (
        db.query(models.Technika).filter(models.Technika.id == item_id).first()
    )
    if not item:
        raise HTTPException(status_code=404, detail="Техніку не знайдено")

    old_ts = (item.avtomobil or item.derj_nomer or "").strip()
    data_dict = data.model_dump()
    misce_zberiganny = data_dict.pop("misce_zberiganny", None)

    # Перевіряємо, що контрагент та екіпаж існують в базі даних
    validate_technika_linked_fields(data_dict, db)

    for key, value in data_dict.items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)

    new_ts = (item.avtomobil or item.derj_nomer or "").strip()

    # Якщо змінився номер/назва авто — оновлюємо ts у dop_data_technika
    if old_ts and new_ts and old_ts != new_ts:
        db.query(models.DopDataTechnika).filter(
            models.DopDataTechnika.ts == old_ts
        ).update({"ts": new_ts}, synchronize_session=False)

    # Синхронізуємо або оновлюємо габарити в dop_data_technika
    if new_ts:
        existing_dop = (
            db.query(models.DopDataTechnika)
            .filter(models.DopDataTechnika.ts == new_ts)
            .first()
        )
        if existing_dop:
            existing_dop.d = item.d
            existing_dop.w = item.w
            existing_dop.v = item.v
            existing_dop.rik = item.rik
            existing_dop.vin = item.vin
            if misce_zberiganny is not None:
                existing_dop.misce_zberiganny = misce_zberiganny

            # Якщо всі габарити стерті користувачем — видаляємо порожній рядок з dop_data_technika
            has_any_data = any([
                (existing_dop.d or "").strip(),
                (existing_dop.w or "").strip(),
                (existing_dop.v or "").strip(),
                (existing_dop.rik or "").strip(),
                (existing_dop.vin or "").strip(),
                (existing_dop.misce_zberiganny or "").strip(),
            ])
            if not has_any_data:
                db.delete(existing_dop)
        else:
            if any([item.d, item.w, item.v, item.rik, item.vin, misce_zberiganny]):
                db.add(
                    models.DopDataTechnika(
                        ts=new_ts,
                        rik=item.rik,
                        vin=item.vin,
                        d=item.d,
                        w=item.w,
                        v=item.v,
                        misce_zberiganny=misce_zberiganny,
                    )
                )
    db.commit()
    return enrich_technika(item, db)


@app.delete("/api/technika/{item_id}", tags=["5. Technika"])
def delete_technika(item_id: int, db: Session = Depends(get_db)):
    item = (
        db.query(models.Technika).filter(models.Technika.id == item_id).first()
    )
    if not item:
        raise HTTPException(status_code=404, detail="Техніку не знайдено")

    ts_keys = [t.strip() for t in [item.avtomobil, item.derj_nomer, item.vin] if t and t.strip()]
    if ts_keys:
        db.query(models.DopDataTechnika).filter(
            (models.DopDataTechnika.ts.in_(ts_keys))
            | (models.DopDataTechnika.vin.in_(ts_keys))
        ).delete(synchronize_session=False)

    db.delete(item)
    db.commit()
    return {"status": "success", "message": f"Техніку #{item_id} та пов'язані габарити в dop_data_technika видалено"}


# ==========================================
# 6. API: Dop Data Technika
# ==========================================
@app.get(
    "/api/dop_data_technika/",
    response_model=List[schemas.DopDataTechnikaResponse],
    tags=["6. Dop Data Technika"],
)
def get_dop_data_technika_list(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(models.DopDataTechnika)
    if search:
        query = query.filter(
            (models.DopDataTechnika.ts.ilike(f"%{search}%"))
            | (models.DopDataTechnika.vin.ilike(f"%{search}%"))
            | (models.DopDataTechnika.misce_zberiganny.ilike(f"%{search}%"))
        )
    return query.offset(skip).limit(limit).all()


@app.get(
    "/api/dop_data_technika/{item_id}",
    response_model=schemas.DopDataTechnikaResponse,
    tags=["6. Dop Data Technika"],
)
def get_dop_data_technika_item(item_id: int, db: Session = Depends(get_db)):
    item = (
        db.query(models.DopDataTechnika)
        .filter(models.DopDataTechnika.id == item_id)
        .first()
    )
    if not item:
        raise HTTPException(
            status_code=404, detail="Запис додаткових даних техніки не знайдено"
        )
    return item


@app.post(
    "/api/dop_data_technika/",
    response_model=schemas.DopDataTechnikaResponse,
    status_code=201,
    tags=["6. Dop Data Technika"],
)
def create_dop_data_technika(
    data: schemas.DopDataTechnikaCreate, db: Session = Depends(get_db)
):
    item = models.DopDataTechnika(**data.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)

    # Двостороння синхронізація: якщо існує запис у technika з таким ТС — оновлюємо його габарити
    if item.ts:
        clean_ts = item.ts.strip()
        autos = db.query(models.Technika).filter(
            (models.Technika.avtomobil == clean_ts) | (models.Technika.derj_nomer == clean_ts)
        ).all()
        for auto in autos:
            if item.rik: auto.rik = item.rik
            if item.vin: auto.vin = item.vin
            if item.d: auto.d = item.d
            if item.w: auto.w = item.w
            if item.v: auto.v = item.v
        db.commit()

    return item


@app.put(
    "/api/dop_data_technika/{item_id}",
    response_model=schemas.DopDataTechnikaResponse,
    tags=["6. Dop Data Technika"],
)
def update_dop_data_technika(
    item_id: int,
    data: schemas.DopDataTechnikaUpdate,
    db: Session = Depends(get_db),
):
    item = (
        db.query(models.DopDataTechnika)
        .filter(models.DopDataTechnika.id == item_id)
        .first()
    )
    if not item:
        raise HTTPException(
            status_code=404, detail="Запис додаткових даних техніки не знайдено"
        )

    old_ts = (item.ts or "").strip()
    for key, value in data.model_dump().items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)

    # Двостороння синхронізація: оновлюємо пов'язані записи в technika
    ts_list = [t for t in [old_ts, (item.ts or "").strip()] if t]
    if ts_list:
        autos = db.query(models.Technika).filter(
            (models.Technika.avtomobil.in_(ts_list)) | (models.Technika.derj_nomer.in_(ts_list))
        ).all()
        for auto in autos:
            auto.rik = item.rik
            auto.vin = item.vin
            auto.d = item.d
            auto.w = item.w
            auto.v = item.v
        db.commit()

    return item


@app.delete("/api/dop_data_technika/{item_id}", tags=["6. Dop Data Technika"])
def delete_dop_data_technika(item_id: int, db: Session = Depends(get_db)):
    item = (
        db.query(models.DopDataTechnika)
        .filter(models.DopDataTechnika.id == item_id)
        .first()
    )
    if not item:
        raise HTTPException(
            status_code=404, detail="Запис додаткових даних техніки не знайдено"
        )
    ts_val = (item.ts or "").strip()
    db.delete(item)
    db.commit()

    # Двостороннє очищення: очищаємо габарити у відповідній техніці
    if ts_val:
        autos = db.query(models.Technika).filter(
            (models.Technika.avtomobil == ts_val) | (models.Technika.derj_nomer == ts_val)
        ).all()
        for auto in autos:
            auto.d = None
            auto.w = None
            auto.v = None
        db.commit()

    return {
        "status": "success",
        "message": f"Додаткові дані техніки #{item_id} та пов'язані габарити видалено",
    }


# ==========================================
# 7. API: Nomenklatyra (Культури / Вантажі)
# ==========================================
@app.get(
    "/api/nomenklatyra/",
    response_model=List[schemas.NomenklatyraResponse],
    tags=["7. Nomenklatyra"],
)
def get_nomenklatyra_list(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(models.Nomenklatyra)
    if search:
        query = query.filter(
            (models.Nomenklatyra.name.ilike(f"%{search}%"))
            | (models.Nomenklatyra.code.ilike(f"%{search}%"))
            | (models.Nomenklatyra.type.ilike(f"%{search}%"))
            | (models.Nomenklatyra.vpv_1_3.ilike(f"%{search}%"))
        )
    return query.offset(skip).limit(limit).all()


@app.get(
    "/api/nomenklatyra/{item_id}",
    response_model=schemas.NomenklatyraResponse,
    tags=["7. Nomenklatyra"],
)
def get_nomenklatyra_item(item_id: int, db: Session = Depends(get_db)):
    item = (
        db.query(models.Nomenklatyra)
        .filter(models.Nomenklatyra.id == item_id)
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail="Товар/культуру не знайдено")
    return item


@app.post(
    "/api/nomenklatyra/",
    response_model=schemas.NomenklatyraResponse,
    status_code=201,
    tags=["7. Nomenklatyra"],
)
def create_nomenklatyra(
    data: schemas.NomenklatyraCreate, db: Session = Depends(get_db)
):
    item = models.Nomenklatyra(**data.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@app.put(
    "/api/nomenklatyra/{item_id}",
    response_model=schemas.NomenklatyraResponse,
    tags=["7. Nomenklatyra"],
)
def update_nomenklatyra(
    item_id: int,
    data: schemas.NomenklatyraUpdate,
    db: Session = Depends(get_db),
):
    item = (
        db.query(models.Nomenklatyra)
        .filter(models.Nomenklatyra.id == item_id)
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail="Товар/культуру не знайдено")

    old_names = [n.strip() for n in [item.name, item.code] if n and n.strip()]

    for key, value in data.model_dump().items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)

    # Якщо назва вантажу змінилася — оновлюємо закріплену культуру в place.crop (place ⟷ nomenklatyra)
    if old_names and item.name:
        db.query(models.Place).filter(
            models.Place.crop.in_(old_names)
        ).update({"crop": item.name}, synchronize_session=False)
        db.commit()

    return item


@app.delete("/api/nomenklatyra/{item_id}", tags=["7. Nomenklatyra"])
def delete_nomenklatyra(item_id: int, db: Session = Depends(get_db)):
    item = (
        db.query(models.Nomenklatyra)
        .filter(models.Nomenklatyra.id == item_id)
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail="Товар/культуру не знайдено")

    names = [n.strip() for n in [item.name, item.code] if n and n.strip()]

    # Очищаємо прив'язку культури/вантажу в точках завантаження (place)
    if names:
        db.query(models.Place).filter(
            models.Place.crop.in_(names)
        ).update({"crop": None}, synchronize_session=False)

    db.delete(item)
    db.commit()
    return {"status": "success", "message": f"Номенклатуру #{item_id} та пов'язані посилання в складах видалено"}


# ==========================================
# 8. TTN & Interconnected Services
# ==========================================

# ==========================================
# Export All Database Tables (Full JSON Dump)
# ==========================================
@app.get("/api/export/all", tags=["Database Export"])
def export_all_database(db: Session = Depends(get_db)):
    """Повертає повний JSON дамп усіх 7 таблиць бази даних."""
    return {
        "kontragents": [x.to_dict() for x in db.query(models.Kontragent).all()],
        "data_info": [x.to_dict() for x in db.query(models.DataInfo).all()],
        "people": [x.to_dict() for x in db.query(models.Person).all()],
        "place": [x.to_dict() for x in db.query(models.Place).all()],
        "technika": [x.to_dict() for x in db.query(models.Technika).all()],
        "dop_data_technika": [
            x.to_dict() for x in db.query(models.DopDataTechnika).all()
        ],
        "nomenklatyra": [
            x.to_dict() for x in db.query(models.Nomenklatyra).all()
        ],
    }


if __name__ == "__main__":
    import uvicorn

    print("=" * 60)
    print("Сервер успішно запущено!")
    print("Веб-інтерфейс:     http://127.0.0.1:8000")
    print("Документація API:  http://127.0.0.1:8000/docs")
    print("=" * 60)
    uvicorn.run(app, host="0.0.0.0", port=8000)
