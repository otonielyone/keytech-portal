from models.users import User, SessionLocal, Base, engine

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

db = SessionLocal()

# Check if user exists
user = db.query(User).filter(User.username == "toni.yone").first()

if not user:
    user = User(username="toni.yone", role="admin")
    user.set_password("admin123")  # ✅ now this works without errors
    db.add(user)
    db.commit()
    print("Toni Yone added as admin!")
else:
    print("User already exists:", user.username)

db.close()
