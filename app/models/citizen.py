from datetime import datetime
from typing import List, Optional, Tuple

from pydantic import BaseModel, validator, Schema, conlist, Extra


class Citizen(BaseModel):
    citizen_id: int = Schema(..., gt=0)
    town: str = Schema(..., min_length=1, max_length=256)
    street: str = Schema(..., min_length=1, max_length=256)
    building: str = Schema(..., min_length=1, max_length=256)
    apartment: int = Schema(..., gt=0)
    name: str = Schema(..., min_length=1, max_length=256)
    birth_date: datetime = Schema(...)
    gender: str = Schema(..., regex="^(male|female)$")
    relatives: List[int] = Schema([])  # todo: validate by whole set somehow


class CitizenIn(Citizen):
    @validator("birth_date", pre=True)
    def validate_birth_date(cls, birth_date: str):  # noqa: cls/self in pydantic
        birth_date = datetime.strptime(birth_date, "%d.%m.%Y")
        if birth_date > datetime.today():
            raise ValueError("birth_date can't be less than today")
        return birth_date

    class Config:
        extra = Extra.forbid


# /imports
class CitizensImportsIn(BaseModel):
    citizens: conlist(CitizenIn, min_items=1)


class CitizensImportsOutData(BaseModel):
    import_id: int

    class Config:
        orm_mode = True


class CitizensImportsOut(BaseModel):
    data: CitizensImportsOutData


# /imports/{import_id}/citizens/{citizen_id}
class CitizenUpdateIn(BaseModel):
    town: str = Schema(None, min_length=1, max_length=256)
    street: str = Schema(None, min_length=1, max_length=256)
    building: str = Schema(None, min_length=1, max_length=256)
    apartment: int = Schema(None, gt=0)
    name: str = Schema(None, min_length=1, max_length=256)
    birth_date: str = None
    gender: str = Schema(None, regex="^(male|female)$")
    relatives: List[int] = None

    @validator("birth_date", pre=True)
    def validate_birth_date(cls, birth_date: str):  # noqa: cls/self in pydantic
        birth_date = datetime.strptime(birth_date, "%d.%m.%Y")
        if birth_date < datetime.today():
            raise ValueError("birth_date can't be less than today")
        return birth_date

    class Config:
        extra = Extra.forbid


def validate_citizen_update(citizen: CitizenUpdateIn) -> Tuple[bool, Optional[str]]:
    if len(citizen.dict()) < 1:
        return True, "You must specify at least 1 field"
    return False, None


class CitizenUpdateOut(BaseModel):
    data: Citizen

    class Config:
        json_encoders = {datetime: lambda v: v.strftime("%d.%m.%Y")}


# /imports/{import_id}/citizens
class CitizensGetOut(BaseModel):
    data: List[Citizen]

    class Config:
        json_encoders = {datetime: lambda v: v.strftime("%d.%m.%Y")}


# /imports/{import_id}/citizens/birthdays
class CitizenGiftCounter(BaseModel):
    citizen_id: int
    presents: int


class CitizensPresentsCalendar(BaseModel):
    m_1: List[CitizenGiftCounter] = Schema([], alias="1")
    m_2: List[CitizenGiftCounter] = Schema([], alias="2")
    m_3: List[CitizenGiftCounter] = Schema([], alias="3")
    m_4: List[CitizenGiftCounter] = Schema([], alias="4")
    m_5: List[CitizenGiftCounter] = Schema([], alias="5")
    m_6: List[CitizenGiftCounter] = Schema([], alias="6")
    m_7: List[CitizenGiftCounter] = Schema([], alias="7")
    m_8: List[CitizenGiftCounter] = Schema([], alias="8")
    m_9: List[CitizenGiftCounter] = Schema([], alias="9")
    m_10: List[CitizenGiftCounter] = Schema([], alias="10")
    m_11: List[CitizenGiftCounter] = Schema([], alias="11")
    m_12: List[CitizenGiftCounter] = Schema([], alias="12")


class CitizensPresentsOut(BaseModel):
    data: CitizensPresentsCalendar


# /imports/{import_id}/towns/stat/percentile/age
class CitizensAgeStatByTown(BaseModel):
    town: str
    p50: float
    p75: float
    p99: float


class CitizensAgeStatsOut(BaseModel):
    data: List[CitizensAgeStatByTown]
