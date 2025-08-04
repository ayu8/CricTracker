from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date
from .models import YesorNo, InningType, MatchResult

class UserBase(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[int] = None

class MatchBase(BaseModel):
    date: date
    ground: str
    came_to_bat: YesorNo
    batting_position: Optional[int] = None
    runs_scored: Optional[int] = None
    balls_faced: Optional[int] = None
    fours: Optional[int] = None
    sixes: Optional[int] = None
    out: Optional[YesorNo] = None
    match_inning: Optional[InningType] = None
    catches: int = 0
    run_outs: int = 0
    stumpings: int = 0
    overs_bowled: Optional[float] = None
    runs_conceded: Optional[int] = None
    wickets: Optional[int] = None
    wides: Optional[int] = None
    no_balls: Optional[int] = None
    match_result: MatchResult

class MatchCreate(MatchBase):
    pass

class MatchResponse(MatchBase):
    match_id: int

    class Config:
        from_attributes = True

class MatchUpdate(BaseModel):
    date: Optional[date] = None
    ground: Optional[str] = None
    came_to_bat: Optional[YesorNo] = None
    batting_position: Optional[int] = None
    runs: Optional[int] = None
    balls: Optional[int] = None
    fours: Optional[int] = None
    sixes: Optional[int] = None
    out: Optional[YesorNo] = None
    match_inning: Optional[InningType] = None
    catches: Optional[int] = None
    run_outs: Optional[int] = None
    stumpings: Optional[int] = None
    overs_bowled: Optional[float] = None
    runs_conceded: Optional[int] = None
    wickets: Optional[int] = None
    wides: Optional[int] = None
    no_balls: Optional[int] = None
    match_result: Optional[MatchResult] = None

class BattingStatsResponse(BaseModel):
    matches: int
    innings: int
    runs_scored: int
    balls_faced: int
    fours: int
    sixes: int
    batting_average: Optional[float]
    batting_strike_rate: Optional[float]
    highest_score: Optional[int]
    balls_per_boundary: Optional[float]
    thirties: int
    fifties: int
    hundreds: int
    thirties_plus: int
    ducks: int
    matches_won: int
    win_pct: Optional[float]

class LimitedBattingStatsResponse(BaseModel):
    matches: int
    innings: int
    runs_scored: int
    batting_average: Optional[float]
    batting_strike_rate: Optional[float]
    highest_score: Optional[int]

class BattingInningWiseResponse(BattingStatsResponse):
    inning_type: str

class BattingMatchResultWiseResponse(BattingStatsResponse):
    match_result: str

class BattingPositionWiseResponse(BattingStatsResponse):
    batting_position: Optional[int] = None

class BattingGroundWiseResponse(BattingStatsResponse):
    ground: str

class BowlingStatsResponse(BaseModel):
    matches: int
    innings: int
    overs_bowled: float
    runs_conceded: int
    wickets_taken: int
    bowling_average: Optional[float]
    bowling_strike_rate: Optional[float]
    economy_rate: Optional[float]
    best_bowling: Optional[str]
    three_fers: int
    five_fers: int
    catches: int
    runouts: int
    stumpings: int
    dismissals_per_match: Optional[float]

class LimitedBowlingStatsResponse(BaseModel):
    matches: int
    innings: int
    overs_bowled: float
    runs_conceded: int
    wickets_taken: int

class BowlingInningWiseResponse(BowlingStatsResponse):
    inning_type: str

class BowlingMatchResultWiseResponse(BowlingStatsResponse):
    match_result: str

class BowlingGroundWiseResponse(BowlingStatsResponse):
    ground: str
