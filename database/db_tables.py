from Sent_anlys.database.db_config import engine  # Adjusted path
from Sent_anlys.database.db_models import Base 

if __name__ == "__main__":
    try:
        print("Creating tables...")
        Base.metadata.create_all(bind=engine)
        print("Tables created successfully!")
    except Exception as e:
        print(f"Error: {e}")
