from collections import defaultdict
from datetime import datetime
from typing import List, Dict

import numpy
from sqlalchemy.orm import Session

from app.db_models.citizen import Citizen, Import, Relations
from app.models.citizen import (
    CitizenIn as CitizenModel,
    CitizenUpdateIn as CitizenUpdateModel,
)


def get_citizens_by_import_id(db: Session, import_id: int) -> List[Citizen]:
    return db.query(Citizen).filter(Citizen.import_id == import_id).all()


def get_citizen(db: Session, import_id: int, citizen_id: int) -> Citizen:
    return (
        db.query(Citizen)
        .filter(Citizen.import_id == import_id, Citizen.citizen_id == citizen_id)
        .first()
    )


def add_relation(db: Session, import_id: int, id_from: int, id_to: int):
    citizen_relation_from = Relations(
        import_id=import_id, citizen_id=id_from, relative_citizen_id=id_to
    )
    citizen_relation_to = Relations(
        import_id=import_id, citizen_id=id_to, relative_citizen_id=id_from
    )
    db.add(citizen_relation_from)
    db.add(citizen_relation_to)


def remove_relation(db: Session, import_id: int, id_from: int, id_to: int):
    relation_from = (
        db.query(Relations)
        .filter(
            Relations.import_id == import_id,
            Relations.citizen_id == id_from,
            Relations.relative_citizen_id == id_to,
        )
        .first()
    )
    relation_to = (
        db.query(Relations)
        .filter(
            Relations.import_id == import_id,
            Relations.citizen_id == id_to,
            Relations.relative_citizen_id == id_from,
        )
        .first()
    )
    db.delete(relation_from)
    db.delete(relation_to)


def import_users(db: Session, citizens: List[CitizenModel]) -> Import:
    inverted_inserted_relations = defaultdict(list)

    db_users_import = Import()
    db.add(db_users_import)
    db.commit()
    db.refresh(db_users_import)
    for citizen in citizens:
        db_citizen = Citizen(
            import_id=db_users_import.import_id,
            citizen_id=citizen.citizen_id,
            town=citizen.town,
            street=citizen.street,
            building=citizen.building,
            apartment=citizen.apartment,
            name=citizen.name,
            birth_date=citizen.birth_date,
            gender=citizen.gender,
        )

        for relative_citizen_id in citizen.relatives:
            if relative_citizen_id in inverted_inserted_relations[citizen.citizen_id]:
                continue
            add_relation(
                db, db_users_import.import_id, citizen.citizen_id, relative_citizen_id
            )
            inverted_inserted_relations[relative_citizen_id].append(citizen.citizen_id)
        db.add(db_citizen)
    db.commit()

    return db_users_import


def update_citizen(
    db: Session, db_citizen: Citizen, update_model: CitizenUpdateModel
) -> Citizen:
    update_data = update_model.dict(skip_defaults=True)

    to_update = {k: v for k, v in update_data.items() if k != "relatives"}
    db.query(Citizen).filter_by(id=db_citizen.id).update(to_update)

    if "relatives" in update_data:
        current_relatives = {rel.relative_citizen_id for rel in db_citizen.relatives}
        relatives_to_remove = current_relatives - set(update_model.relatives)
        relatives_to_create = set(update_model.relatives) - current_relatives
        for rel_id in relatives_to_remove:
            remove_relation(db, db_citizen.import_id, db_citizen.citizen_id, rel_id)
        for rel_id in relatives_to_create:
            add_relation(db, db_citizen.import_id, db_citizen.citizen_id, rel_id)

    db.add(db_citizen)
    db.commit()
    db.refresh(db_citizen)
    return db_citizen


def get_citizens_presents(db: Session, import_id: int) -> Dict[str, List[Dict]]:
    birthdays_presents = {}
    for month_number in range(1, 13):
        birthdays_presents[str(month_number)] = []
        for citizen in get_citizens_by_import_id(db, import_id):
            presents_counter = 0
            for rel in citizen.relatives:
                relative = get_citizen(db, import_id, rel.relative_citizen_id)
                if relative.birth_date.month != month_number:
                    continue
                presents_counter += 1
            if presents_counter == 0:
                continue
            birthdays_presents[str(month_number)].append(
                {"citizen_id": citizen.citizen_id, "presents": presents_counter}
            )
    return birthdays_presents


def calculate_age(born: datetime):
    today = datetime.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))


def get_age_stats_by_town(db: Session, import_id: int) -> List[Dict]:
    stats_by_town = []
    towns = (
        db.query(Citizen.town)
        .filter(Citizen.import_id == import_id)
        .group_by(Citizen.town)
        .all()
    )
    towns = [t.town for t in towns]
    for town in towns:
        citizens = (
            db.query(Citizen.birth_date)
            .filter(Citizen.import_id == import_id, Citizen.town == town)
            .all()
        )
        ages = [calculate_age(c.birth_date) for c in citizens]
        percentiles = numpy.percentile(ages, [50, 75, 99], interpolation="linear")
        stats_by_town.append(
            {
                "town": town,
                "p50": round(percentiles[0], 2),
                "p75": round(percentiles[1], 2),
                "p99": round(percentiles[2], 2),
            }
        )
    return stats_by_town
