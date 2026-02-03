from mentee import create_app, db
from mentee.models import User, JournalEntry, UserIdentity
from datetime import datetime, timedelta
import random

app = create_app()

with app.app_context():
    print("--- 1. Wiping Old Database ---")
    db.drop_all()
    
    print("--- 2. Creating New Schema (SQLite Compatible) ---")
    db.create_all()

    # Create User (Make sure to change password if needed)
    user = User(email="test@elite.com", name="Aniket Narayan Biswas", password="password")
    db.session.add(user)
    db.session.commit()

    # Create Identity
    identity = UserIdentity(
        user_id=user.id,
        archetype_name="The Relentless Architect",
        core_traits=["Stoic", "Analytical", "High-Risk"]
    )
    db.session.add(identity)

    print("--- 3. Seeding Calendar Data ---")
    today = datetime.utcnow()
    moods = ['fire', 'happy', 'calm', 'neutral', 'stressed']
    
    for i in range(20):
        entry_date = today - timedelta(days=20-i)
        date_str = entry_date.strftime('%Y-%m-%d')
        
        entry = JournalEntry(
            user_id=user.id,
            date=date_str,
            mood=random.choice(moods),
            performance_score=random.randint(5, 10),
            content={
                "micro_win": "Fixed the database schema.",
                "reflection": "Learning that simplicity is key in engineering.",
                "brain_dump_mode": False
            }
        )
        db.session.add(entry)

    db.session.commit()
    print("✅ SUCCESS: Database repaired and seeded.")
    print("👉 Now run: python run.py")