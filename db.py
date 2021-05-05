from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref, sessionmaker, joinedload
from datetime import datetime
import random
import string
from config import cfg

engine = create_engine("mysql+pymysql://" +
                       cfg["db"]["user"] + ":" +
                       cfg["db"]["passwd"] + "@" +
                       cfg["db"]["host"] + "/" +
                       cfg["db"]["db"] + "?charset=utf8mb4")

Base = declarative_base()


class Stations(Base):
    __tablename__ = 'stations'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    warning_threshold = Column(Integer, nullable=False)
    danger_threshold = Column(Integer, nullable=False)

    def __repr__(self):
        return "<Stations(id='%s', name='%s', warning_threshold='%s', danger_threshold='%s')>" % (
            self.id, self.name, self.warning_threshold, self.danger_threshold)


class StationsHistory(Base):
    __tablename__ = 'stations_history'
    station_id = Column(Integer, ForeignKey(Stations.id), primary_key=True)
    station = relationship("Stations", backref=backref('stations_history'))
    instant = Column(TIMESTAMP, nullable=False)
    total_people = Column(Integer, nullable=False)

    def __repr__(self):
        return "<StationsHistory(id='%s', station_id='%s', instant='%s', total_people='%s')>" % (
            self.id, self.station_id, self.instant, self.total_people)


class LastUpdate(Base):
    __tablename__ = 'lastupdate'
    uuid = Column(String(32), primary_key=True, nullable=False)
    last_battery = Column(String(100), nullable=False)
    last_update = Column(TIMESTAMP, nullable=False)

    last_position = Column(Integer, ForeignKey(Stations.id))
    station = relationship("Stations", backref=backref('lastupdate'))

    last_position_change = Column(TIMESTAMP, nullable=False)
    total_people = Column(Integer, nullable=False)

    def __repr__(self):
        return "<LastUpdate(uuid='%s', last_battery='%s', last_update='%s', last_position='%s', last_position_change='%s', total_people='%s')>" % (
            self.uuid, self.last_battery, self.last_update, self.last_position, self.last_position_change, self.total_people)


class Skiipass(Base):
    __tablename__ = 'skiipass'
    uuid = Column(String(32), primary_key=True, nullable=False)
    departure_time = Column(TIMESTAMP, primary_key=True, nullable=False)
    arrival_time = Column(TIMESTAMP, nullable=False)

    station_id = Column(Integer, ForeignKey(Stations.id))
    station = relationship("Stations", backref=backref('skiipass'))

    total_people = Column(Integer, nullable=False)

    def __repr__(self):
        return "<Skiipass(name='%s', fullname='%s', password'%s')>" % (
            self.name, self.fullname, self.password)


if __name__ == '__main__':
    # Creates a new session to the database by using the engine we described.
    Session = sessionmaker(bind=engine)
    session = Session()

    station = Stations(name='station 1', warning_threshold=1, danger_threshold=1)
    session.add(station)
    session.commit()

    stations_history = StationsHistory(station=station, instant=datetime.now(), total_people=1)
    session.add(stations_history)
    session.commit()

    # printing lowercase
    letters = string.ascii_lowercase
    randUUID = ''.join(random.choice(letters) for i in range(10))
    last_update = LastUpdate(uuid=randUUID, last_battery="FF", last_update=datetime.now(), station=station,
                             last_position_change=datetime.now(), total_people=1)
    session.add(last_update)
    session.commit()

    skiipass = Skiipass(uuid='station 1', departure_time=datetime.now(), arrival_time=datetime.now(), station=station,
                        total_people=1)
    session.add(skiipass)
    session.commit()
