from fastapi import APIRouter, Depends, HTTPException, status
from backend.database import get_db
from sqlalchemy.orm import Session
from backend.schemas import BattingStatsResponse, LimitedBattingStatsResponse
from backend.models import Match, User
from .jwt import get_current_user
from typing import List


batsman_router = APIRouter()

def calc_batting_stats(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    all_matches_played = db.query(Match).filter(Match.user_id == current_user.user_id).all()

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
    stats = calc_batting_stats(db, current_user)

    return LimitedBattingStatsResponse(**stats)

@batsman_router.get("/get_full_batting_stats", response_model=BattingStatsResponse)
def get_full_batting_stats(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    stats = calc_batting_stats(db, current_user)

    return BattingStatsResponse(**stats)


# @batsman_router.get("/innings", response_model=List[BattingStatsResponse])
# def get_innings_stats(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
#     results = []
#     for inning in ["first", "second"]:
#         matches = db.query(Match).filter(Match.inning.ilike(inning)).all()
#         results.append(calculate_segment_stats(matches, segment_name=inning))
#     return results

# @batsman_router.get("/results", response_model=List[BattingStatsResponse])
# def get_result_stats(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
#     results = []
#     for result in ["Won", "Lost", "No Result"]:
#         matches = db.query(Match).filter(Match.match_result == result).all()
#         results.append(calculate_segment_stats(matches, segment_name=result))
#     return results

# @batsman_router.get("/positions", response_model=List[BattingStatsResponse])
# def get_position_stats(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
#     positions = db.query(Match.batting_position).distinct().all()
#     results = []
#     for pos in positions:
#         if pos is not None:
#             matches = db.query(Match).filter(Match.batting_position == pos[0]).all()
#             results.append(calculate_segment_stats(matches, segment_name=f"At {pos[0]}"))
#     return results

# @batsman_router.get("/grounds", response_model=List[BattingStatsResponse])
# def get_ground_stats(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
#     # Get distinct ground names (extract first element from each tuple)
#     grounds = [g[0] for g in db.query(Match.ground).distinct().all() if g[0] is not None]
    
#     results = []
#     for ground in grounds:
#         matches = db.query(Match).filter(Match.ground == ground).all()  # Use exact match
#         results.append(calculate_segment_stats(matches, segment_name=f"{ground}"))
#     return results

# # This is a helper function to avoid code duplication
# def calculate_segment_stats(matches: List[Match], segment_name: str):
#     if not matches:  # Handle empty match lists
#         return {
#             "segment": segment_name,
#             "matches": 0,
#             "innings": 0,
#             "runs_scored": 0,
#             "balls_faced": 0,
#             "fours": 0,
#             "sixes": 0,
#             "highest_score": None,
#             "batting_average": None,
#             "batting_strike_rate": None,
#             "balls_per_boundary": None,
#             "num_30s": 0,
#             "num_50s": 0,
#             "num_30plus": 0,
#             "ducks": 0,
#             "matches_won": 0,
#             "win_pct": None
#         }
    
#     inning = 0
#     total_runs_scored = 0
#     total_balls_played = 0
#     total_fours = 0
#     total_sixes = 0
#     highest_score = 0
#     total_dismissals_batting = 0
#     total_30s = 0
#     total_50s = 0
#     total_30plus = 0
#     total_won = 0
#     ducks = 0

#     for match in matches:
#         if match.came_to_bat:
#             inning += 1
#         total_runs_scored += match.runs_scored
#         total_balls_played += match.balls_faced
#         total_fours += match.fours
#         total_sixes += match.sixes
#         highest_score = max(highest_score, match.runs_scored)
#         if match.runs_scored > 29:
#             total_30s += 1
#             total_30plus += 1
#             if match.runs_scored > 49:
#                 total_50s += 1
#                 total_30s -= 1
#         if match.match_result == "Won":
#             total_won += 1
#         if match.out:
#             total_dismissals_batting += 1
#             if (match.runs_scored == 0):
#                 ducks += 1

#     batting_average = (total_runs_scored / total_dismissals_batting) if total_dismissals_batting else None
#     batting_strike_rate = (total_runs_scored / total_balls_played) * 100 if total_balls_played else None
#     balls_per_boundary = (total_balls_played / (total_fours + total_sixes)) if (total_fours + total_sixes) else None
#     win_pct = (total_won / len(matches)) * 100 if matches else None   

#     return {
#         "segment": segment_name,  # Added to identify the segment
#         "matches": len(matches),
#         "innings": inning,
#         "runs_scored": total_runs_scored,
#         "balls_faced": total_balls_played,
#         "fours": total_fours,
#         "sixes": total_sixes,
#         "highest_score": highest_score,
#         "batting_average": round(batting_average, 2) if batting_average else None,
#         "batting_strike_rate": round(batting_strike_rate, 2) if batting_strike_rate else None,
#         "balls_per_boundary": round(balls_per_boundary, 2) if balls_per_boundary else None,
#         "num_30s": total_30s,
#         "num_50s": total_50s,
#         "num_30plus": total_30plus,
#         "ducks": ducks,
#         "matches_won": total_won,
#         "win_pct": round(win_pct, 2) if win_pct is not None else None
#     }