from fastapi import APIRouter, Depends, HTTPException, status
from backend.database import get_db
from sqlalchemy.orm import Session
from backend.schemas import MatchCreate, MatchResponse, MatchUpdate
from backend.models import Match, User
from .jwt import get_current_user

match_router = APIRouter()

@match_router.post("/add_match", response_model=MatchResponse)
def create_match(match: MatchCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    new_match_data = match.dict()
    new_match_data['user_id'] = current_user.user_id  # Set the user_id from the authenticated user
    db_match = Match(**new_match_data)
    db.add(db_match)
    db.commit()
    db.refresh(db_match)
    return db_match

@match_router.get("/get_all_matches", response_model=list[MatchResponse])
def get_matches(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Only return matches that belong to the current user
    return db.query(Match).filter(Match.user_id == current_user.user_id).all()

@match_router.get("/get_match/{match_id}", response_model=MatchResponse)
def get_single_match(match_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Two-step verification process
    # Step 1: Check if match exists at all
    db_match = db.query(Match).filter(Match.match_id == match_id).first()
    if not db_match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Match with ID {match_id} not found"
        )
    
    # Step 2: Check if match belongs to current user
    if db_match.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view someone else's match"
        )
    
    return db_match

@match_router.delete("/delete_match/{match_id}", response_model=dict)
def delete_match(match_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Two-step verification process
    # Step 1: Check if match exists at all
    db_match = db.query(Match).filter(Match.match_id == match_id).first()
    if not db_match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Match with ID {match_id} not found"
        )
    
    # Step 2: Check if match belongs to current user
    if db_match.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete this match"
        )
    
    db.delete(db_match)
    db.commit()
    return {"message": "Match deleted successfully"}

@match_router.patch("/update_match/{match_id}", response_model=MatchResponse)
def update_match(match_id: int, match: MatchUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        # Two-step verification process
        # Step 1: Check if match exists at all
        db_match = db.query(Match).filter(Match.match_id == match_id).first()
        if not db_match:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Match with ID {match_id} not found"
            )
        
        # Step 2: Check if match belongs to current user
        if db_match.user_id != current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to update this match"
            )

        # Get the raw dictionary and filter out unset and None values
        update_data = {}
        for field, value in match.dict().items():
            # Only include fields that were explicitly set and are not None
            if field in match.model_fields_set and value is not None:
                update_data[field] = value
        
        # Prevent user from changing the user_id (security measure)
        if 'user_id' in update_data:
            del update_data['user_id']
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You cannot change the user_id of a match"
            )
        
        # Update only the provided non-None fields
        for field, value in update_data.items():
            setattr(db_match, field, value)

        db.commit()
        db.refresh(db_match)
        return db_match
    except HTTPException:
        # Re-raise HTTP exceptions (our custom 404/403 errors)
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error updating match: {str(e)}"
        )
