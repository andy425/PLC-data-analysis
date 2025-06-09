from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, Float, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()


class CycleTime(Base):
    __tablename__ = 'cycle_times'
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    cell = Column(Integer, index=True)
    cycle_time = Column(Float)


class CellStatus(Base):
    __tablename__ = 'cell_statuses'
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    cell = Column(Integer, index=True)
    status = Column(Integer)


def init_db(url='sqlite:///plc_data.db'):
    engine = create_engine(url)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)
