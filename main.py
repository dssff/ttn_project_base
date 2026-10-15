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

        if db.query(models.Place).count() == 0:
            db.add(
                models.Place(
                    name="Східне Поле №12",
                    owner="Агро-Трейд",
                    area="145.8 га",
                    crop="Пшениця озима",
                    people="Шевченко Іван Олексійович",
                )
            )

        if db.query(models.Technika).count() == 0:
            db.add(
                models.Technika(
                    avtomobil="Тягач",
                    misce_ystanovky="Гараж №1",
                    derj_nomer="AX1234CA",
                    vin="WMA06XZZ8LP987654",
                    d="12.5",
                    w="2.5",
                    rik="2021",
                    v="85",
                    ekipaj="Шевченко І.О.",
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
                    ts="Тягач MAN",
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

    # Якщо ім'я контрагента змінилося — синхронізуємо поле object у data_info
    if old_names and old_names[0] != new_obj_name:
        db.query(models.DataInfo).filter(
            models.DataInfo.object.in_(old_names)
        ).update({"object": new_obj_name}, synchronize_session=False)

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

    # Знаходимо всі варіанти назв контрагента для очищення data_info
    names = [n.strip() for n in [item.name, item.full_name, f"Контрагент #{item.id}"] if n and n.strip()]

    # Спочатку видаляємо всі пов'язані записи з таблиці data_info
    if names:
        db.query(models.DataInfo).filter(
            models.DataInfo.object.in_(names)
        ).delete(synchronize_session=False)

    # Видаляємо сам запис контрагента
    db.delete(item)
    db.commit()
    return {
        "status": "success",
        "message": f"Контрагента #{item_id} та пов'язані дані в data_info видалено",
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
    for key, value in data.model_dump().items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return item


@app.delete("/api/people/{item_id}", tags=["3. People"])
def delete_person(item_id: int, db: Session = Depends(get_db)):
    item = db.query(models.Person).filter(models.Person.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Запис особи не знайдено")
    db.delete(item)
    db.commit()
    return {"status": "success", "message": f"Особу #{item_id} видалено"}


# ==========================================
# 4. API: Place
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
        )
    return query.offset(skip).limit(limit).all()


@app.get(
    "/api/place/{item_id}",
    response_model=schemas.PlaceResponse,
    tags=["4. Place"],
)
def get_place(item_id: int, db: Session = Depends(get_db)):
    item = db.query(models.Place).filter(models.Place.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Місце / поле не знайдено")
    return item


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
    return item


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
    return item


@app.delete("/api/place/{item_id}", tags=["4. Place"])
def delete_place(item_id: int, db: Session = Depends(get_db)):
    item = db.query(models.Place).filter(models.Place.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Місце / поле не знайдено")
    db.delete(item)
    db.commit()
    return {"status": "success", "message": f"Місце #{item_id} видалено"}


# ==========================================
# 5. API: Technika
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
        )
    return query.offset(skip).limit(limit).all()


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
    return item


@app.post(
    "/api/technika/",
    response_model=schemas.TechnikaResponse,
    status_code=201,
    tags=["5. Technika"],
)
def create_technika(
    data: schemas.TechnikaCreate, db: Session = Depends(get_db)
):
    item = models.Technika(**data.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


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
    for key, value in data.model_dump().items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return item


@app.delete("/api/technika/{item_id}", tags=["5. Technika"])
def delete_technika(item_id: int, db: Session = Depends(get_db)):
    item = (
        db.query(models.Technika).filter(models.Technika.id == item_id).first()
    )
    if not item:
        raise HTTPException(status_code=404, detail="Техніку не знайдено")
    db.delete(item)
    db.commit()
    return {"status": "success", "message": f"Техніку #{item_id} видалено"}


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
    for key, value in data.model_dump().items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
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
    db.delete(item)
    db.commit()
    return {
        "status": "success",
        "message": f"Додаткові дані техніки #{item_id} видалено",
    }


# ==========================================
# Export All Database Tables (Full JSON Dump)
# ==========================================
@app.get("/api/export/all", tags=["Database Export"])
def export_all_database(db: Session = Depends(get_db)):
    """Повертає повний JSON дамп усіх 6 таблиць локальної бази даних."""
    return {
        "kontragents": [x.to_dict() for x in db.query(models.Kontragent).all()],
        "data_info": [x.to_dict() for x in db.query(models.DataInfo).all()],
        "people": [x.to_dict() for x in db.query(models.Person).all()],
        "place": [x.to_dict() for x in db.query(models.Place).all()],
        "technika": [x.to_dict() for x in db.query(models.Technika).all()],
        "dop_data_technika": [
            x.to_dict() for x in db.query(models.DopDataTechnika).all()
        ],
    }


if __name__ == "__main__":
    import uvicorn

    print("=" * 60)
    print("Сервер успішно запущено!")
    print("Веб-інтерфейс:     http://127.0.0.1:8000")
    print("Документація API:  http://127.0.0.1:8000/docs")
    print("=" * 60)
    uvicorn.run(app, host="127.0.0.1", port=8000)
