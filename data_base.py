from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("db_url")
Base = declarative_base()


class Vehicle(Base):
    __tablename__ = "vehicles"
    year = Column(Integer, primary_key=True, index=True)
    make = Column(String(255), primary_key=True, index=True)
    model = Column(String(255), primary_key=True, index=True)
    specific_model = Column(String(255), primary_key=True)
    curb_weight = Column(Float)


engine = create_engine(DATABASE_URL, echo=False, pool_size=20, max_overflow=0)
SessionLocal = sessionmaker(bind=engine)


def create_tables():
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    create_tables()
