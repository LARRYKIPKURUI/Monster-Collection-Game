from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from lib.models import Base
import os
import logging

# Configure logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)

DB_PATH = 'sqlite:///monster_game.db'
engine = create_engine(DB_PATH, echo=False)
Session = sessionmaker(bind=engine)

def init_db(drop_existing=False):
    """Initialize database with optional dropping of existing tables"""
    try:
        if drop_existing and os.path.exists('monster_game.db'):
            os.remove('monster_game.db')
        Base.metadata.create_all(engine)
        print("✅ Database initialized successfully!")
        return True
    except Exception as e:
        print(f"❌ Database initialization failed: {str(e)}")
        return False

def get_session():
    """Provide a new database session with error handling"""
    try:
        return Session()
    except Exception as e:
        print(f"❌ Failed to create database session: {str(e)}")
        return None

if __name__ == '__main__':
    init_db(drop_existing=True)