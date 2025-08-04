from fastapi import APIRouter, Depends, HTTPException, status
from backend.database import get_db
from sqlalchemy.orm import Session
from backend.schemas import BattingStatsResponse, LimitedBattingStatsResponse, BattingGroundWiseResponse, BattingInningWiseResponse, BattingMatchResultWiseResponse, BattingPositionWiseResponse
from backend.models import Match, User, InningType, MatchResult
from .jwt import get_current_user
from typing import List


batsman_router = APIRouter()

def calc_batting_stats(db: Session = Depends(get_db), current_user: User = Depends(get_current_user), matches: List[Match] = None):
    all_matches_played = matches

    total_innings = 0
    total_runs_scored = 0
    total_balls_played = 0
    total_fours = 0
    total_sixes = 0
    highest_score = 0
    total_dismissals_batting = 0
    total_ducks = 0
    total_30s = 0
    total_50s = 0
    total_100s = 0
    total_30plus = 0
    total_won = 0
    total_lost = 0
    total_no_result = 0

    for match in all_matches_played:
        if match.came_to_bat.value.lower() == "yes":
            total_innings += 1
        total_runs_scored += match.runs_scored
        total_balls_played += match.balls_faced
        total_fours += match.fours
        total_sixes += match.sixes
        highest_score = max(highest_score, match.runs_scored)
        if match.runs_scored > 29:
            total_30s += 1
            total_30plus += 1
            if match.runs_scored > 49:
                total_50s += 1
                total_30s -= 1
                if match.runs_scored > 99:
                    total_100s += 1
                    total_50s -= 1
        if match.match_result.value.lower() == "won":
            total_won += 1
        elif match.match_result.value.lower() == "lost":
            total_lost += 1
        else:
            total_no_result += 1
        
        if match.out.value.lower() == "yes":
            total_dismissals_batting += 1
            if (match.runs_scored == 0):
                total_ducks += 1

    batting_average = (total_runs_scored / total_dismissals_batting) if total_dismissals_batting else None
    batting_strike_rate = (total_runs_scored / total_balls_played) * 100 if total_balls_played else None
    balls_per_boundary = (total_balls_played / (total_fours + total_sixes)) if (total_fours + total_sixes) else None
    win_pct = (total_won / len(all_matches_played)) * 100 if all_matches_played else None   

    return {
        "matches": len(all_matches_played),
        "innings": total_innings,
        "runs_scored": total_runs_scored,
        "balls_faced": total_balls_played,
        "fours": total_fours,
        "sixes": total_sixes,
        "highest_score": highest_score,
        "batting_average": round(batting_average, 2) if batting_average else None,
        "batting_strike_rate": round(batting_strike_rate, 2) if batting_strike_rate else None,
        "thirties": total_30s,
        "fifties": total_50s,
        "hundreds": total_100s,
        "thirties_plus": total_30plus,
        "balls_per_boundary": round(balls_per_boundary, 2) if balls_per_boundary else None,
        "ducks": total_ducks,
        "matches_won": total_won,
        "win_pct": round(win_pct, 2) if win_pct is not None else None
    }

@batsman_router.get("/get_limited_batting_stats", response_model=LimitedBattingStatsResponse)
def get_limited_batting_stats(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    all_matches_played = db.query(Match).filter(Match.user_id == current_user.user_id).all()
    stats = calc_batting_stats(db, current_user, all_matches_played)

    return LimitedBattingStatsResponse(**stats)

@batsman_router.get("/get_full_batting_stats", response_model=BattingStatsResponse)
def get_full_batting_stats(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    all_matches_played = db.query(Match).filter(Match.user_id == current_user.user_id).all()
    stats = calc_batting_stats(db, current_user, all_matches_played)

    return BattingStatsResponse(**stats)

@batsman_router.get("/get_inning_stats", response_model=List[BattingInningWiseResponse])
def get_inning_stats(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    results = []
    for inning in [InningType.FIRST, InningType.SECOND]:
        matches = db.query(Match).filter(
            Match.user_id == current_user.user_id,
            Match.match_inning == inning
        ).all()
        stats = calc_batting_stats(db, current_user, matches)
        stats["inning_type"] = inning.value.upper()
        results.append(stats)

    return results


@batsman_router.get("/get_match-result_stats", response_model=List[BattingMatchResultWiseResponse])
def get_match_result_stats(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    results = []
    for result in [MatchResult.WON, MatchResult.LOST, MatchResult.NO_RESULT]:
        matches = db.query(Match).filter(
            Match.user_id == current_user.user_id,
            Match.match_result == result
        ).all()
        stats = calc_batting_stats(db, current_user, matches)
        stats["match_result"] = result.value.upper()
        results.append(stats)

    return results


@batsman_router.get("/get_positions_stats", response_model=List[BattingPositionWiseResponse])
def get_position_stats(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    positions = db.query(Match.batting_position).filter(Match.user_id == current_user.user_id).distinct().all()
    results = []
    for pos in positions:
        print(f"pos: {pos}")  # Debugging line to check the content of pos
        print(f"pos[0]: {pos[0]}")  # pos is a tuple, extract the first element
        # pos is a tuple, extract the first element
        if pos[0] is not None:
            matches = db.query(Match).filter(
                Match.user_id == current_user.user_id,
                Match.batting_position == pos[0]
            ).all()
            stats = calc_batting_stats(db, current_user, matches)
            stats["batting_position"] = pos[0]
            results.append(stats)
    return results

@batsman_router.get("/get_grounds_stats", response_model=List[BattingGroundWiseResponse])
def get_ground_stats(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    grounds = db.query(Match.ground).filter(Match.user_id == current_user.user_id).distinct().all()
    results = []
    for ground in grounds:
        if ground[0] is not None:  # Check ground[0] since ground is a tuple
            matches = db.query(Match).filter(
                Match.user_id == current_user.user_id,
                Match.ground == ground[0]
            ).all()
            stats = calc_batting_stats(db, current_user, matches)
            stats["ground"] = ground[0]  # Add ground name to the response
            results.append(stats)
    return results