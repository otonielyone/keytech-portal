from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker
import os
from datetime import datetime
from passlib.context import CryptContext

# -------------------------
# Database setup
# -------------------------

DATABASE_PATH = "/var/www/html/keytech/database/users.db"
os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

# admin  → full access
# user   → inventory access
# guest  → login only, no inventory access

class User(Base):
    __tablename__ = "users"
    
    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String(80), unique=True, index=True, nullable=False)
    role = Column(String(20), nullable=False, default="guest")
    password_hash = Column(String(255), nullable=False)
    created = Column(String(100), default=lambda: datetime.utcnow().isoformat())

    def set_password(self, password: str):
        self.password_hash = pwd_context.hash(password)  # no length limit

    def verify_password(self, password: str):
        return pwd_context.verify(password, self.password_hash)
    
    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.user_id)

    def __repr__(self):
        return f"<User {self.username}>"

def create_database():
    Base.metadata.create_all(bind=engine)
    print("Created User Database!")

create_database()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
