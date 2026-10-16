from typing import Optional
from pydantic import BaseModel, ConfigDict


# ==========================================
# 1. Kontragents
# ==========================================
class KontragentBase(BaseModel):
    medcode: Optional[str] = None
    name: Optional[str] = None
    full_name: Optional[str] = None
    ipn: Optional[str] = None
    endpou: Optional[str] = None
    ur_fiz: Optional[str] = None


class KontragentCreate(KontragentBase):
    ur_address: Optional[str] = None
    phone: Optional[str] = None
    fax: Optional[str] = None


class KontragentUpdate(KontragentBase):
    ur_address: Optional[str] = None
    phone: Optional[str] = None
    fax: Optional[str] = None


class KontragentResponse(KontragentBase):
    id: int
    ur_address: Optional[str] = None
    phone: Optional[str] = None
    fax: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


# ==========================================
# 2. Data Info
# ==========================================
class DataInfoBase(BaseModel):
    object: Optional[str] = None
    type: Optional[str] = None
    k: Optional[str] = None
    v: Optional[str] = None


class DataInfoCreate(DataInfoBase):
    pass


class DataInfoUpdate(DataInfoBase):
    pass


class DataInfoResponse(DataInfoBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


# ==========================================
# 3. People
# ==========================================
class PersonBase(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None
    full_name: Optional[str] = None


class PersonCreate(PersonBase):
    pass


class PersonUpdate(PersonBase):
    pass


class PersonResponse(PersonBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


# ==========================================
# 4. Place
# ==========================================
class PlaceBase(BaseModel):
    name: Optional[str] = None
    owner: Optional[str] = None
    area: Optional[str] = None
    crop: Optional[str] = None
    people: Optional[str] = None


class PlaceCreate(PlaceBase):
    pass


class PlaceUpdate(PlaceBase):
    pass


class PlaceResponse(PlaceBase):
    id: int
    people_info: Optional[dict] = None
    crop_info: Optional[dict] = None
    model_config = ConfigDict(from_attributes=True)


# ==========================================
# 5. Technika
# ==========================================
class TechnikaBase(BaseModel):
    avtomobil: Optional[str] = None
    misce_ystanovky: Optional[str] = None
    derj_nomer: Optional[str] = None
    vin: Optional[str] = None
    d: Optional[str] = None
    w: Optional[str] = None
    rik: Optional[str] = None
    v: Optional[str] = None
    ekipaj: Optional[str] = None
    telefony: Optional[str] = None
    pricep: Optional[str] = None
    kontragent: Optional[str] = None
    model: Optional[str] = None
    kolir: Optional[str] = None
    telegram: Optional[str] = None
    medcode: Optional[str] = None
    wialon_id: Optional[str] = None
    dodatkovo: Optional[str] = None


class TechnikaCreate(TechnikaBase):
    misce_zberiganny: Optional[str] = None


class TechnikaUpdate(TechnikaBase):
    misce_zberiganny: Optional[str] = None


class TechnikaResponse(TechnikaBase):
    id: int
    misce_zberiganny: Optional[str] = None
    dop_data: Optional[dict] = None
    kontragent_info: Optional[dict] = None
    vodiy_info: Optional[dict] = None
    model_config = ConfigDict(from_attributes=True)


# ==========================================
# 6. Dop Data Technika
# ==========================================
class DopDataTechnikaBase(BaseModel):
    ts: Optional[str] = None
    rik: Optional[str] = None
    vin: Optional[str] = None
    d: Optional[str] = None
    w: Optional[str] = None
    v: Optional[str] = None
    misce_zberiganny: Optional[str] = None


class DopDataTechnikaCreate(DopDataTechnikaBase):
    pass


class DopDataTechnikaUpdate(DopDataTechnikaBase):
    pass


class DopDataTechnikaResponse(DopDataTechnikaBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


# ==========================================
# 7. Nomenklatyra (Номенклатура / Вантажі)
# ==========================================
class NomenklatyraBase(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None
    type: Optional[str] = None
    od_vym: Optional[str] = None
    vpv_1_3: Optional[str] = None
    dodatkovo: Optional[str] = None


class NomenklatyraCreate(NomenklatyraBase):
    pass


class NomenklatyraUpdate(NomenklatyraBase):
    pass


class NomenklatyraResponse(NomenklatyraBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


# ==========================================
# 8. TTN Auto Fill Combined Response
# ==========================================
class TTNAutoFillResponse(BaseModel):
    avtomobil: Optional[str] = None
    derj_nomer: Optional[str] = None
    model: Optional[str] = None
    pricep: Optional[str] = None
    gabaryty: Optional[dict] = None  # d, w, v, rik, vin, misce_zberiganny
    pereviznyk: Optional[dict] = None  # kontragent info + ur_address
    vodiy: Optional[dict] = None  # people info (name, full_name, code)
    punkt_navantazhennya: Optional[dict] = None  # place info
    komirnyk_zdav: Optional[dict] = None  # responsible person at place
    vantazh_nomenklatyra: Optional[dict] = None  # crop with vpv_1_3

