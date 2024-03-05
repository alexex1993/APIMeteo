from typing import List

import uvicorn
import databases
import sqlalchemy
import datetime
from fastapi import FastAPI
from pydantic import BaseModel

# SQLAlchemy specific code, as with any other app
DATABASE_URL = "sqlite:///./meteo.db"

database = databases.Database(DATABASE_URL)

metadata = sqlalchemy.MetaData()

wr = sqlalchemy.Table(
    "weather_readings",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("dttm", sqlalchemy.DateTime),
    sqlalchemy.Column("temp", sqlalchemy.Float),
    sqlalchemy.Column("hum", sqlalchemy.Float),
    sqlalchemy.Column("pres", sqlalchemy.Float),
)


engine = sqlalchemy.create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
metadata.create_all(engine)


class WeatherReadingsIn(BaseModel):
    temp: float
    hum: float
    pres: float


class WeatherReadings(BaseModel):
    id: int
    dttm: datetime.datetime
    temp: float
    hum: float
    pres: float


app = FastAPI()

@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.get("/weather/", response_model=List[WeatherReadings])
async def read_notes():
    query = wr.select()
    return await database.fetch_all(query)


@app.post("/weather/", response_model=WeatherReadings)
async def create_note(note: WeatherReadingsIn):
    query = wr.insert().values(temp=note.temp, hum=note.hum, pres=note.pres)
    last_record_id = await database.execute(query)
    print(query)
    return {**note.dict(), "id": last_record_id, "dttm": datetime.datetime.now()}


if __name__ == "__main__":
    uvicorn.run(app, host="192.168.0.200", port=8000)