"""
Update database schema with User model
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.database import engine
from models.database import Base

def update_schema():
    """Create all tables"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Database schema updated successfully!")

if __name__ == "__main__":
    update_schema() 