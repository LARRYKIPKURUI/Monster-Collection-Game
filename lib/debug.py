from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from lib.models import Base 

engine = create_engine('sqlite:///mydatabase.db')

# Creating a configured "Session" class
Session = sessionmaker(bind=engine)

# Function to initialize DB schema
def init_db():
    Base.metadata.create_all(engine)


if __name__ == '__main__':
    init_db()
