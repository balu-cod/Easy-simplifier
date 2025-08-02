from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional

from config.settings import settings

class MongoDB:
    client: Optional[AsyncIOMotorClient] = None
    database = None

mongodb = MongoDB()

async def connect_to_mongo():
    """Create database connection"""
    try:
        mongodb.client = AsyncIOMotorClient(settings.MONGODB_URL)
        mongodb.database = mongodb.client.get_database()
        
        # Test the connection
        await mongodb.client.admin.command('ping')
        print("✅ MongoDB connected successfully")
    except Exception as e:
        print(f"❌ Failed to connect to MongoDB: {e}")
        raise

async def close_mongo_connection():
    """Close database connection"""
    if mongodb.client:
        mongodb.client.close()
        print("👋 MongoDB connection closed")

def get_mongo_db():
    """Dependency to get MongoDB database"""
    return mongodb.database

async def init_mongo():
    """Initialize MongoDB connection"""
    await connect_to_mongo()
    
    # Create indexes for better performance
    try:
        db = mongodb.database
        
        # Images collection indexes
        await db.images.create_index([("user_id", 1), ("upload_date", -1)])
        await db.images.create_index([("is_public", 1), ("upload_date", -1)])
        await db.images.create_index([("tags", 1)])
        
        # Game sessions indexes
        await db.game_sessions.create_index([("user_id", 1), ("game_type", 1)])
        await db.game_sessions.create_index([("game_type", 1), ("score", -1)])
        await db.game_sessions.create_index([("start_time", -1)])
        
        # Chat history indexes
        await db.chat_history.create_index([("user_id", 1), ("timestamp", -1)])
        
        # Feedback indexes
        await db.feedback.create_index([("user_id", 1), ("created_at", -1)])
        await db.feedback.create_index([("type", 1), ("created_at", -1)])
        
        print("✅ MongoDB indexes created successfully")
    except Exception as e:
        print(f"⚠️ Warning: Failed to create MongoDB indexes: {e}")
        # Don't raise - indexes are not critical for basic functionality