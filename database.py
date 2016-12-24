#!/usr/bin/python

# Ctrl-O Node Database Python Code
# This is used by ctrl-o code to access local sqlite database
# Uses SQLAlchemy to try and make logic easier to understand and change
# 
#
# Author: Patrick Shields
# Copyright Owner: Random Wire Technologies, LLC 2016
#
#

from sqlalchemy import create_engine, Table, Column, Integer, String, ForeignKey, or_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker,relationship

import time
import os
import logging
import subprocess

Base = declarative_base()
engine = None
session = None

# logger = logging.getLogger(__name__)
# logger.setLevel(logging.INFO)
# handler = logging.FileHandler('/var/log/nfc.log')
# handler.setLevel(logging.INFO)
# formatter = logging.Formatter('(%(levelname)s) %(asctime)s %(message)s','%Y-%m-%d %H:%M:%S')
# handler.setFormatter(formatter)
# logger.addHandler(handler)

def setup():
    global Base
    global engine
    global session
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

# Define Objects

card_group_table = Table('card_group', Base.metadata,
    Column('card_id', Integer, ForeignKey('cards.id')),
    Column('group_id', Integer, ForeignKey('groups.id'))
)

class Card(Base):
    __tablename__ = 'cards'
    id = Column(Integer, primary_key=True)
    serial = Column(String)

    access = relationship("Access", back_populates="card")
    group = relationship("Group", secondary=card_group_table)

    def __repr__(self):
        return "<Card(id= '%s', serial='%s')>" % (self.id, self.serial)

class Group(Base):
    __tablename__ = 'groups'
    id = Column(Integer, primary_key=True)
    name = Column(String)

    access = relationship("Access", back_populates="group")
    card = relationship("Card", secondary=card_group_table)

class Schedule(Base):
    __tablename__ = 'schedules'
    id = Column(Integer, primary_key=True)
    name = Column(String)

    times = relationship("ScheduleTime", back_populates="schedule")
    access = relationship("Access", back_populates="schedule")

    def __repr__(self):
        return "<Schedule(id= '%s', name='%s')>" % (self.id, self.name)

class ScheduleTime(Base):
    __tablename__ = 'schedule_times'
    id = Column(Integer, primary_key=True)
    schedule_id = Column(ForeignKey('schedules.id'))
    day_of_week = Column(Integer)
    start_ts = Column(Integer)
    end_ts = Column(Integer)
    start_minutes = Column(Integer)
    end_minutes = Column(Integer)

    schedule = relationship("Schedule", back_populates="times")


    def __repr__(self):
        return "<ScheduleTime(Schedule='%s' DOW=%s Start=%s End=%s StartMin=%s EndMin=%s)>" % (self.id, self.day_of_week, self.start_ts,self.end_ts,self.start_minutes,self.end_minutes)

class Access(Base):
    __tablename__ = 'access'
    id = Column(Integer, primary_key=True)
    card_id = Column(ForeignKey('cards.id'))
    group_id = Column(ForeignKey('groups.id'))
    schedule_id = Column(ForeignKey('schedules.id'))

    card = relationship("Card", back_populates="access")
    schedule = relationship("Schedule", back_populates="access")
    group = relationship("Group", back_populates="access")

    def __repr__(self):
        return "<Access(id='%s', card_id='%s', schedule_id='%s')>" % (self.id, self.card_id, self.schedule_id)



def check_access(serial):
    global session
    now = time.localtime()
    dow = now.tm_wday
    minute = now.tm_hour*60 + now.tm_min
    ts = int(time.time())
    card = session.query(Card).filter(Card.serial == serial).one()
    print("Found Card:%s"%serial)
    access = session.query(Access)\
        .filter(Access.schedule.has(Schedule.times.any(or_(ScheduleTime.day_of_week==dow, ScheduleTime.day_of_week==None))))\
        .filter(Access.schedule.has(Schedule.times.any(or_(ScheduleTime.start_ts < ts, ScheduleTime.start_ts == None))))\
        .filter(Access.schedule.has(Schedule.times.any(or_(ScheduleTime.end_ts > ts, ScheduleTime.end_ts == None))))\
        .filter(Access.schedule.has(Schedule.times.any(or_(ScheduleTime.start_minutes <= minute, ScheduleTime.start_minutes == None))))\
        .filter(Access.schedule.has(Schedule.times.any(or_(ScheduleTime.end_minutes >= minute, ScheduleTime.end_minutes == None))))\
        .filter(or_(Access.card_id == card.id,Access.card_id == None))\
        .filter(or_(Access.group.has(Group.card.any(Card.id == card.id)),Access.group_id == None))\
        .all()
    print("Found Access(es):\n %s"%access)
    print("Current Time: DOW=%s Minute=%s TS=%s" %(dow,minute,ts))
    accesses = session.query(Access).all()
    for access in accesses:
        print ("Access: (%s) Card_Id=%s Schedule_id=%s" % (access.id,access.card_id,access.schedule_id))
        schedules = session.query(Schedule).filter(Schedule.access.any(Access.id == access.id))
        for schedule in schedules:
            print(" Schedule: %s" % schedule.name)
            for times in session.query(ScheduleTime).filter(ScheduleTime.schedule.has(Schedule.id == schedule.id)):
               print ("  Time (%s): DOW=%s Start=%s End=%s StartMin=%s EndMin=%s" % (times.id,times.day_of_week,times.start_ts,times.end_ts,times.start_minutes,times.end_minutes))
    
def add_fake_data():
    global session
    sched = Schedule(name='Anytime')
    sched.times = [ScheduleTime()]
    session.add(sched)
    session.commit()
    sched = Schedule(name='Weekdays')
    sched.times = [ScheduleTime(day_of_week=1),\
        ScheduleTime(day_of_week=2),\
        ScheduleTime(day_of_week=3),\
        ScheduleTime(day_of_week=4),\
        ScheduleTime(day_of_week=5)]
    session.add(sched)
    session.commit()
    card = Card(serial='deadbeef')
    card.access = [Access(schedule_id = sched.id)]
    session.add(card)
    sched = Schedule(name='Weekends')
    sched.times = [ScheduleTime(day_of_week=6,start_ts=0,end_ts=1500000000,start_minutes=0,end_minutes=1440),\
        ScheduleTime(day_of_week=7, start_ts=0,end_ts=1500000000,start_minutes=0,end_minutes=1440)]
    session.add(sched)
    session.commit()
    card = Card(serial='bedeaded')
    card.access = [Access(schedule_id = sched.id)]
    session.add(card)
    session.commit()
