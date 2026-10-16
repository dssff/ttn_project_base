from sqlalchemy import Column, Integer, String, Text
from database import Base


class Kontragent(Base):
    __tablename__ = "kontragents"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    medcode = Column(String(100), nullable=True)
    name = Column(String(255), nullable=True)
    full_name = Column(String(500), nullable=True)
    ipn = Column(String(50), nullable=True)
    endpou = Column(String(50), nullable=True)
    ur_fiz = Column(String(50), nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "medcode": self.medcode,
            "name": self.name,
            "full_name": self.full_name,
            "ipn": self.ipn,
            "endpou": self.endpou,
            "ur_fiz": self.ur_fiz,
        }


class DataInfo(Base):
    __tablename__ = "data_info"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    object = Column(String(255), nullable=True)
    type = Column(String(100), nullable=True)
    k = Column(String(255), nullable=True)
    v = Column(Text, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "object": self.object,
            "type": self.type,
            "k": self.k,
            "v": self.v,
        }


class Person(Base):
    __tablename__ = "people"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    code = Column(String(100), nullable=True)
    name = Column(String(255), nullable=True)
    full_name = Column(String(500), nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "code": self.code,
            "name": self.name,
            "full_name": self.full_name,
        }


class Place(Base):
    __tablename__ = "place"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=True)
    owner = Column(String(255), nullable=True)
    area = Column(String(100), nullable=True)
    crop = Column(String(255), nullable=True)
    people = Column(String(255), nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "owner": self.owner,
            "area": self.area,
            "crop": self.crop,
            "people": self.people,
        }


class Technika(Base):
    __tablename__ = "technika"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    avtomobil = Column(String(255), nullable=True)
    misce_ystanovky = Column(String(255), nullable=True)
    derj_nomer = Column(String(50), nullable=True)
    vin = Column(String(100), nullable=True)
    d = Column(String(100), nullable=True)
    w = Column(String(100), nullable=True)
    rik = Column(String(50), nullable=True)
    v = Column(String(100), nullable=True)
    ekipaj = Column(String(255), nullable=True)
    telefony = Column(String(255), nullable=True)
    pricep = Column(String(255), nullable=True)
    kontragent = Column(String(255), nullable=True)
    model = Column(String(255), nullable=True)
    kolir = Column(String(100), nullable=True)
    telegram = Column(String(100), nullable=True)
    medcode = Column(String(100), nullable=True)
    wialon_id = Column(String(100), nullable=True)
    dodatkovo = Column(Text, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "avtomobil": self.avtomobil,
            "misce_ystanovky": self.misce_ystanovky,
            "derj_nomer": self.derj_nomer,
            "vin": self.vin,
            "d": self.d,
            "w": self.w,
            "rik": self.rik,
            "v": self.v,
            "ekipaj": self.ekipaj,
            "telefony": self.telefony,
            "pricep": self.pricep,
            "kontragent": self.kontragent,
            "model": self.model,
            "kolir": self.kolir,
            "telegram": self.telegram,
            "medcode": self.medcode,
            "wialon_id": self.wialon_id,
            "dodatkovo": self.dodatkovo,
        }


class DopDataTechnika(Base):
    __tablename__ = "dop_data_technika"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    ts = Column(String(255), nullable=True)
    rik = Column(String(50), nullable=True)
    vin = Column(String(100), nullable=True)
    d = Column(String(100), nullable=True)
    w = Column(String(100), nullable=True)
    v = Column(String(100), nullable=True)
    misce_zberiganny = Column(String(255), nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "ts": self.ts,
            "rik": self.rik,
            "vin": self.vin,
            "d": self.d,
            "w": self.w,
            "v": self.v,
            "misce_zberiganny": self.misce_zberiganny,
        }


class Nomenklatyra(Base):
    __tablename__ = "nomenklatyra"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    code = Column(String(100), nullable=True)
    name = Column(String(255), nullable=True, index=True)
    type = Column(String(100), nullable=True)
    od_vym = Column(String(50), nullable=True)
    vpv_1_3 = Column(String(255), nullable=True)
    dodatkovo = Column(Text, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "code": self.code,
            "name": self.name,
            "type": self.type,
            "od_vym": self.od_vym,
            "vpv_1_3": self.vpv_1_3,
            "dodatkovo": self.dodatkovo,
        }

