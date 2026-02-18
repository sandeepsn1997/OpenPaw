import sys
import os

# Add backend to path
sys.path.append(os.path.abspath("backend"))

from app.db import SessionLocal, init_db
from app.services.conversation import ConversationService
from app.database import Base

def test_list_conversations():
    db = SessionLocal()
    try:
        service = ConversationService(db)
        convs = service.list_conversations()
        print(f"Success! Found {len(convs)} conversations")
        for c in convs:
            print(f"- ID: {c.id}, Messages: {len(c.messages)}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    # Check if we should use backend/openpaw_v2.db
    # Workaround for path
    import app.db
    print(f"Using database: {app.db.DATABASE_URL}")
    
    test_list_conversations()
