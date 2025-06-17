from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Set up the engine and session
engine = create_engine("sqlite:///db/monsters.db")
Session = sessionmaker(bind=engine)
Base = declarative_base()
