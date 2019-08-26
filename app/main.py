from fastapi import FastAPI, Body, Depends
from fastapi.exceptions import RequestValidationError, HTTPException
from starlette.requests import Request
from starlette.responses import Response, PlainTextResponse
from sqlalchemy.orm import Session

from app.models.citizen import (
    CitizensImportsIn,
    CitizensImportsOut,
    CitizenUpdateIn,
    CitizenUpdateOut,
    CitizensGetOut,
    CitizensPresentsOut,
    CitizensAgeStatsOut,
)
from app.tests.api.v1.tests_configs.import_citizens_config import simple_import_data
from app.crud.citizen import (
    import_users,
    get_citizens_by_import_id,
    update_citizen,
    get_citizen,
    get_citizens_presents,
    get_age_stats_by_town,
)
from app.db.session import Session, engine
from app.db.base_class import Base

Base.metadata.create_all(bind=engine)
app = FastAPI()


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return PlainTextResponse(str(exc), status_code=400)


@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    response = Response("Internal server error", status_code=500)
    try:
        request.state.db = Session()
        response = await call_next(request)
    finally:
        request.state.db.close()
    return response


# Dependency
def get_db(request: Request):
    return request.state.db


# 1
@app.post("/imports", response_model=CitizensImportsOut)
async def import_citizens(
    citizens: CitizensImportsIn = Body(..., example=simple_import_data),
    db: Session = Depends(get_db),
):
    return {"data": import_users(db, citizens.citizens)}


# 2
@app.patch(
    "/imports/{import_id}/citizens/{citizen_id}", response_model=CitizenUpdateOut
)
async def update_citizen_info(
    import_id: int,
    citizen_id: int,
    citizen_update_fields: CitizenUpdateIn = Body(...),
    db: Session = Depends(get_db),
):
    db_citizen = get_citizen(db, import_id, citizen_id)
    print(citizen_update_fields)
    if not db_citizen:
        raise HTTPException(status_code=404, detail="Item not found")
    updated_citizen = update_citizen(db, db_citizen, citizen_update_fields)
    updated_citizen = {
        **vars(updated_citizen),
        **{"relatives": [rel.relative_citizen_id for rel in updated_citizen.relatives]},
    }
    return {"data": updated_citizen}


# 3
@app.get("/imports/{import_id}/citizens", response_model=CitizensGetOut)
async def get_citizens(import_id: int, db: Session = Depends(get_db)):
    citizens = get_citizens_by_import_id(db, import_id)
    citizens = [
        {
            **vars(citizen),
            **{"relatives": [rel.relative_citizen_id for rel in citizen.relatives]},
        }
        for citizen in citizens
    ]
    return {"data": citizens}


# 4
@app.get("/imports/{import_id}/citizens/birthdays", response_model=CitizensPresentsOut)
async def get_citizens_presents_calendar(import_id: int, db: Session = Depends(get_db)):
    return {"data": get_citizens_presents(db, import_id)}


# 5
@app.get(
    "/imports/{import_id}/towns/stat/percentile/age", response_model=CitizensAgeStatsOut
)
async def get_citizens_age_stats(import_id: int, db: Session = Depends(get_db)):
    return {"data": get_age_stats_by_town(db, import_id)}
