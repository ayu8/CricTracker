from fastapi import APIRouter, Depends, HTTPException, status
from backend.database import get_db
from sqlalchemy.orm import Session
from backend.schemas import BowlingStatsResponse, LimitedBowlingStatsResponse, BowlingGroundWiseResponse, BowlingInningWiseResponse, BowlingMatchResultWiseResponse
from backend.models import Match, User, InningType, MatchResult
from .jwt import get_current_user
from typing import List
import math


bowler_router = APIRouter()

def calc_bowling_stats(db: Session = Depends(get_db), current_user: User = Depends(get_current_user), matches: List[Match] = None):
    all_matches_played = matches

    total_balls_bowled = 0
    total_overs_bowled = 0
    total_wickets_taken = 0
    total_runs_conceded = 0
    three_fers = 0
    five_fers = 0
    wickets_in_best_bowling = 0
    runs_in_best_bowling = 0
    inning = 0
    catches = 0
    runouts = 0
    stumpings = 0

    for match in all_matches_played:
        if (match.overs_bowled):
            inning += 1
        total_wickets_taken += match.wickets
        if match.wickets:
            if (match.wickets > 4):
                five_fers += 1
            elif (match.wickets > 2):
                three_fers += 1
            if (match.wickets > wickets_in_best_bowling):
                wickets_in_best_bowling = match.wickets
                runs_in_best_bowling = match.runs_conceded
            elif (match.wickets == wickets_in_best_bowling):
                if (match.runs_conceded < runs_in_best_bowling):
                    runs_in_best_bowling = match.runs_conceded
        total_runs_conceded += match.runs_conceded
        total_balls_bowled += math.floor(match.overs_bowled)*6 + (match.overs_bowled - math.floor(match.overs_bowled))*10
        total_overs_bowled = (total_balls_bowled//6) + (total_balls_bowled%6)/10
        catches += match.catches
        runouts += match.run_outs
        stumpings += match.stumpings

    bowling_average = (total_runs_conceded / total_wickets_taken) if total_wickets_taken else None
    economy_rate = (total_runs_conceded / total_balls_bowled)*6 if total_balls_bowled else None
    bowling_strike_rate = (total_balls_bowled / total_wickets_taken) if total_wickets_taken else None
    dismissals_per_match = round((catches + runouts) / len(all_matches_played), 2) if all_matches_played else None

    return {
        "matches": len(all_matches_played),
        "innings": inning,
        "overs_bowled": total_overs_bowled,
        "runs_conceded": total_runs_conceded,
        "wickets_taken": total_wickets_taken,
        "best_bowling": f"{wickets_in_best_bowling}/{runs_in_best_bowling}" if wickets_in_best_bowling else None,
        "three_fers": three_fers,
        "five_fers": five_fers,
        "bowling_average": round(bowling_average, 2) if bowling_average else None,
        "bowling_strike_rate": round(bowling_strike_rate, 2) if bowling_strike_rate else None,
        "economy_rate": round(economy_rate, 2) if economy_rate else None,
        "catches": catches,
        "runouts": runouts,
        "stumpings": stumpings,
        "dismissals_per_match": dismissals_per_match
    }

@bowler_router.get("/get_limited_bowling_stats", response_model=LimitedBowlingStatsResponse)
def get_limited_bowling_stats(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    all_matches_played = db.query(Match).filter(Match.user_id == current_user.user_id).all()
    stats = calc_bowling_stats(db, current_user, all_matches_played)

    return LimitedBowlingStatsResponse(**stats)

@bowler_router.get("/get_full_bowling_stats", response_model=BowlingStatsResponse)
def get_full_bowling_stats(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    all_matches_played = db.query(Match).filter(Match.user_id == current_user.user_id).all()
    stats = calc_bowling_stats(db, current_user, all_matches_played)

    return BowlingStatsResponse(**stats)


@bowler_router.get("/get_inning_stats", response_model=List[BowlingInningWiseResponse])
def get_inning_stats(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    results = []
    for inning in [InningType.FIRST, InningType.SECOND]:
        matches = db.query(Match).filter(
            Match.user_id == current_user.user_id,
            Match.match_inning == inning
        ).all()
        stats = calc_bowling_stats(db, current_user, matches)
        stats["inning_type"] = inning.value.upper()
        results.append(stats)

    return results

@bowler_router.get("/get_match-result_stats", response_model=List[BowlingMatchResultWiseResponse])
def get_match_result_stats(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    results = []
    for result in [MatchResult.WON, MatchResult.LOST, MatchResult.NO_RESULT]:
        matches = db.query(Match).filter(
            Match.user_id == current_user.user_id,
            Match.match_result == result
        ).all()
        stats = calc_bowling_stats(db, current_user, matches)
        stats["match_result"] = result.value.upper()
        results.append(stats)

    return results

@bowler_router.get("/get_grounds_stats", response_model=List[BowlingGroundWiseResponse])
def get_ground_stats(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    grounds = db.query(Match.ground).filter(Match.user_id == current_user.user_id).distinct().all()
    results = []
    for ground in grounds:
        if ground[0] is not None:  # Check ground[0] since ground is a tuple
            matches = db.query(Match).filter(
                Match.user_id == current_user.user_id,
                Match.ground == ground[0]
            ).all()
            stats = calc_bowling_stats(db, current_user, matches)
            stats["ground"] = ground[0]  # Add ground name to the response
            results.append(stats)
    return results