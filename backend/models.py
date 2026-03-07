from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime, timezone

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)

class Settings(Base):
    __tablename__ = 'settings'
    id = Column(Integer, primary_key=True)
    webhook_url = Column(String, nullable=True)

class ZoneAlias(Base):
    __tablename__ = 'zone_aliases'
    zone_id = Column(Integer, primary_key=True) # 1 to 6
    alias = Column(String)
    is_bypassed = Column(Boolean, default=False)

class EventLog(Base):
    __tablename__ = 'event_logs'
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    event_type = Column(String) # 'ZONE_TRIPPED', 'ARMED', 'DISARMED', etc.
    details = Column(String)
