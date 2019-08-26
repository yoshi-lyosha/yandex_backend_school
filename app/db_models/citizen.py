from typing import List

from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class Import(Base):
    import_id = Column(Integer, primary_key=True)


class Relations(Base):
    import_id = Column(Integer, primary_key=True)
    citizen_id = Column(Integer, ForeignKey("citizen.citizen_id"), primary_key=True)
    relative_citizen_id = Column(
        Integer, ForeignKey("citizen.citizen_id"), primary_key=True
    )


class Citizen(Base):
    id = Column(Integer, primary_key=True, index=True)

    import_id = Column(Integer, index=True)
    citizen_id = Column(Integer, index=True)

    town = Column(String)
    street = Column(String)
    building = Column(String)
    apartment = Column(Integer)
    name = Column(String)
    birth_date = Column(DateTime)
    gender = Column(String)
    relatives: List[Relations] = relationship(
        "Relations",
        primaryjoin="and_(Citizen.import_id == Relations.import_id, Citizen.citizen_id == Relations.citizen_id)",
    )
