from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import random
import json
import uuid

from database.postgresql import get_db
from database.mongodb import get_mongo_db
from models.user import User
from middleware.auth import get_current_active_user
from services.game_service import GameService

router = APIRouter()
game_service = GameService()

@router.get("/")
async def get_games():
    """Get all available games"""
    games = [
        {
            "id": "pattern-recognition",
            "name": "Pattern Recognition",
            "description": "Test your ability to recognize and complete visual patterns",
            "category": "Visual",
            "difficulty_levels": ["easy", "medium", "hard", "expert"],
            "max_score": 1000,
            "estimated_time": "5-10 minutes"
        },
        {
            "id": "word-completion",
            "name": "Word Completion",
            "description": "Complete words and phrases from image text",
            "category": "Language",
            "difficulty_levels": ["easy", "medium", "hard"],
            "max_score": 800,
            "estimated_time": "3-7 minutes"
        },
        {
            "id": "spatial-reasoning",
            "name": "Spatial Reasoning",
            "description": "Solve 3D puzzles and spatial challenges",
            "category": "Logic",
            "difficulty_levels": ["easy", "medium", "hard", "expert"],
            "max_score": 1200,
            "estimated_time": "10-15 minutes"
        },
        {
            "id": "math-puzzles",
            "name": "Math Puzzles",
            "description": "Solve mathematical problems from extracted image content",
            "category": "Math",
            "difficulty_levels": ["easy", "medium", "hard"],
            "max_score": 900,
            "estimated_time": "5-12 minutes"
        },
        {
            "id": "memory-match",
            "name": "Memory Match",
            "description": "Match images and patterns from memory",
            "category": "Memory",
            "difficulty_levels": ["easy", "medium", "hard"],
            "max_score": 600,
            "estimated_time": "3-8 minutes"
        }
    ]
    return {"games": games}

@router.post("/{game_type}/start")
async def start_game(
    game_type: str,
    difficulty: str = "medium",
    current_user: User = Depends(get_current_active_user),
    mongo_db = Depends(get_mongo_db)
):
    """Start a new game session"""
    
    # Validate game type
    valid_games = ["pattern-recognition", "word-completion", "spatial-reasoning", "math-puzzles", "memory-match"]
    if game_type not in valid_games:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid game type. Valid types: {', '.join(valid_games)}"
        )
    
    # Generate game session
    session_id = str(uuid.uuid4())
    game_data = await game_service.generate_game_data(game_type, difficulty)
    
    # Save game session to MongoDB
    game_session = {
        "session_id": session_id,
        "user_id": current_user.id,
        "game_type": game_type,
        "difficulty": difficulty,
        "game_data": game_data,
        "start_time": datetime.utcnow(),
        "status": "active",
        "current_question": 0,
        "score": 0,
        "answers": [],
        "time_remaining": game_data.get("time_limit", 600)  # Default 10 minutes
    }
    
    await mongo_db.game_sessions.insert_one(game_session)
    
    # Return first question only (not all answers)
    response_data = {
        "session_id": session_id,
        "game_type": game_type,
        "difficulty": difficulty,
        "total_questions": len(game_data["questions"]),
        "time_limit": game_data.get("time_limit", 600),
        "current_question": game_data["questions"][0] if game_data["questions"] else None
    }
    
    # Remove correct answers from response
    if response_data["current_question"]:
        response_data["current_question"].pop("correct_answer", None)
    
    return response_data

@router.post("/{game_type}/answer")
async def submit_answer(
    game_type: str,
    session_id: str,
    answer: str,
    question_index: int,
    time_taken: Optional[int] = None,
    current_user: User = Depends(get_current_active_user),
    mongo_db = Depends(get_mongo_db),
    db: Session = Depends(get_db)
):
    """Submit an answer for the current question"""
    
    # Get game session
    game_session = await mongo_db.game_sessions.find_one({
        "session_id": session_id,
        "user_id": current_user.id,
        "status": "active"
    })
    
    if not game_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game session not found or already completed"
        )
    
    # Validate question index
    questions = game_session["game_data"]["questions"]
    if question_index >= len(questions):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid question index"
        )
    
    # Check answer
    question = questions[question_index]
    is_correct = await game_service.check_answer(game_type, question, answer)
    
    # Calculate score for this question
    question_score = game_service.calculate_question_score(
        is_correct, 
        game_session["difficulty"], 
        time_taken or 30
    )
    
    # Update game session
    game_session["answers"].append({
        "question_index": question_index,
        "answer": answer,
        "is_correct": is_correct,
        "score": question_score,
        "time_taken": time_taken,
        "timestamp": datetime.utcnow()
    })
    
    game_session["score"] += question_score
    game_session["current_question"] = question_index + 1
    
    # Check if game is completed
    next_question = None
    game_completed = game_session["current_question"] >= len(questions)
    
    if game_completed:
        game_session["status"] = "completed"
        game_session["end_time"] = datetime.utcnow()
        
        # Update user stats
        current_user.total_score += game_session["score"]
        current_user.games_played += 1
        current_user.experience_points += game_session["score"] // 10
        
        # Level up check
        if current_user.experience_points >= (current_user.level * 100):
            current_user.level += 1
        
        db.commit()
        
        # Check for achievements
        achievements = await game_service.check_achievements(current_user, game_session)
        
    else:
        # Get next question
        next_question = questions[game_session["current_question"]].copy()
        next_question.pop("correct_answer", None)  # Remove answer from response
    
    # Update session in database
    await mongo_db.game_sessions.replace_one(
        {"session_id": session_id},
        game_session
    )
    
    response = {
        "is_correct": is_correct,
        "question_score": question_score,
        "total_score": game_session["score"],
        "game_completed": game_completed,
        "next_question": next_question,
        "current_question_number": game_session["current_question"],
        "total_questions": len(questions)
    }
    
    if game_completed:
        response["final_score"] = game_session["score"]
        response["achievements"] = achievements if 'achievements' in locals() else []
        response["rank"] = await game_service.get_user_rank(game_type, game_session["score"])
    
    return response

@router.get("/{game_type}/leaderboard")
async def get_leaderboard(
    game_type: str,
    limit: int = 10,
    timeframe: str = "all_time",  # all_time, weekly, monthly
    mongo_db = Depends(get_mongo_db)
):
    """Get game leaderboard"""
    
    # Define time filter
    time_filter = {}
    if timeframe == "weekly":
        time_filter = {"end_time": {"$gte": datetime.utcnow() - timedelta(days=7)}}
    elif timeframe == "monthly":
        time_filter = {"end_time": {"$gte": datetime.utcnow() - timedelta(days=30)}}
    
    # Aggregate pipeline for leaderboard
    pipeline = [
        {
            "$match": {
                "game_type": game_type,
                "status": "completed",
                **time_filter
            }
        },
        {
            "$group": {
                "_id": "$user_id",
                "best_score": {"$max": "$score"},
                "games_played": {"$sum": 1},
                "avg_score": {"$avg": "$score"},
                "last_played": {"$max": "$end_time"}
            }
        },
        {
            "$sort": {"best_score": -1}
        },
        {
            "$limit": limit
        }
    ]
    
    leaderboard_data = []
    async for entry in mongo_db.game_sessions.aggregate(pipeline):
        # Get user info (in a real app, you'd join with user collection)
        leaderboard_data.append({
            "user_id": entry["_id"],
            "best_score": entry["best_score"],
            "games_played": entry["games_played"],
            "avg_score": round(entry["avg_score"], 1),
            "last_played": entry["last_played"]
        })
    
    return {
        "game_type": game_type,
        "timeframe": timeframe,
        "leaderboard": leaderboard_data
    }

@router.get("/{game_type}/stats")
async def get_game_stats(
    game_type: str,
    current_user: User = Depends(get_current_active_user),
    mongo_db = Depends(get_mongo_db)
):
    """Get user's game statistics"""
    
    # Aggregate user's game data
    pipeline = [
        {
            "$match": {
                "game_type": game_type,
                "user_id": current_user.id,
                "status": "completed"
            }
        },
        {
            "$group": {
                "_id": "$difficulty",
                "games_played": {"$sum": 1},
                "total_score": {"$sum": "$score"},
                "best_score": {"$max": "$score"},
                "avg_score": {"$avg": "$score"},
                "total_time": {"$sum": {"$subtract": ["$end_time", "$start_time"]}}
            }
        }
    ]
    
    stats_by_difficulty = {}
    async for stat in mongo_db.game_sessions.aggregate(pipeline):
        stats_by_difficulty[stat["_id"]] = {
            "games_played": stat["games_played"],
            "total_score": stat["total_score"],
            "best_score": stat["best_score"],
            "avg_score": round(stat["avg_score"], 1),
            "avg_time_minutes": round(stat["total_time"] / stat["games_played"] / 60000, 1)  # Convert ms to minutes
        }
    
    # Get recent games
    recent_games = []
    async for game in mongo_db.game_sessions.find(
        {"game_type": game_type, "user_id": current_user.id, "status": "completed"},
        sort=[("end_time", -1)],
        limit=5
    ):
        recent_games.append({
            "date": game["end_time"],
            "difficulty": game["difficulty"],
            "score": game["score"],
            "duration_minutes": round((game["end_time"] - game["start_time"]).total_seconds() / 60, 1)
        })
    
    return {
        "game_type": game_type,
        "stats_by_difficulty": stats_by_difficulty,
        "recent_games": recent_games
    }

@router.get("/daily-challenge")
async def get_daily_challenge(
    current_user: User = Depends(get_current_active_user),
    mongo_db = Depends(get_mongo_db)
):
    """Get today's daily challenge"""
    
    today = datetime.utcnow().date()
    
    # Check if user already completed today's challenge
    completed_today = await mongo_db.game_sessions.find_one({
        "user_id": current_user.id,
        "game_type": "daily-challenge",
        "start_time": {
            "$gte": datetime.combine(today, datetime.min.time()),
            "$lt": datetime.combine(today + timedelta(days=1), datetime.min.time())
        },
        "status": "completed"
    })
    
    # Generate daily challenge (same for all users on the same day)
    challenge_data = await game_service.generate_daily_challenge(today)
    
    return {
        "date": today.isoformat(),
        "challenge": challenge_data,
        "completed": bool(completed_today),
        "completion_reward": 100,  # Bonus points for daily challenge
        "streak_bonus": await game_service.get_user_streak(current_user.id, mongo_db)
    }

@router.get("/achievements")
async def get_achievements(
    current_user: User = Depends(get_current_active_user),
    mongo_db = Depends(get_mongo_db)
):
    """Get user's achievements"""
    
    # Get user's achievements from game sessions
    user_achievements = await game_service.get_user_achievements(current_user.id, mongo_db)
    
    # Available achievements
    all_achievements = [
        {
            "id": "first_game",
            "name": "First Steps",
            "description": "Complete your first game",
            "icon": "🎮",
            "points": 10
        },
        {
            "id": "high_scorer",
            "name": "High Scorer",
            "description": "Score over 800 points in any game",
            "icon": "🏆",
            "points": 50
        },
        {
            "id": "speed_demon",
            "name": "Speed Demon",
            "description": "Complete a game in under 3 minutes",
            "icon": "⚡",
            "points": 30
        },
        {
            "id": "perfectionist",
            "name": "Perfectionist",
            "description": "Get 100% accuracy in a game",
            "icon": "💯",
            "points": 40
        },
        {
            "id": "daily_champion",
            "name": "Daily Champion",
            "description": "Complete 7 daily challenges",
            "icon": "📅",
            "points": 70
        },
        {
            "id": "master_player",
            "name": "Master Player",
            "description": "Reach level 10",
            "icon": "👑",
            "points": 100
        }
    ]
    
    # Mark which achievements are unlocked
    for achievement in all_achievements:
        achievement["unlocked"] = achievement["id"] in user_achievements
        if achievement["unlocked"]:
            achievement["unlocked_date"] = user_achievements[achievement["id"]].get("date")
    
    return {
        "achievements": all_achievements,
        "total_unlocked": len(user_achievements),
        "total_points": sum(a["points"] for a in all_achievements if a["unlocked"])
    }