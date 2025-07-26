from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Float, Text, Date, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from .database import Base

class InningType(enum.Enum):
    FIRST = "first"
    SECOND = "second"

class MatchResult(enum.Enum):
    WON = "won"
    LOST = "lost"
    TIE = "tie"
    NO_RESULT = "no_result"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # match_stats = relationship("MatchStats", back_populates="user")

'''
class MatchStats(Base):
    __tablename__ = "match_stats"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    batting_position = Column(Integer, nullable=True)
    runs_scored = Column(Integer, nullable=True)
    balls_faced = Column(Integer, nullable=True)
    fours = Column(Integer, nullable=True)
    sixes = Column(Integer, nullable=True)
    out = Column(Boolean, nullable=True)
    inning = Column(Enum(InningType))
    catches = Column(Integer, default=0)
    run_outs = Column(Integer, default=0)
    overs_bowled = Column(Float, nullable=True)
    runs_conceded = Column(Integer, nullable=True)
    wickets = Column(Integer, nullable=True)
    wides = Column(Integer, nullable=True)
    no_balls = Column(Integer, nullable=True)
    bowling_comments = Column(Text, nullable=True)
    match_result = Column(Enum(MatchResult))

    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    user = relationship("User", back_populates="match_stats")
'''