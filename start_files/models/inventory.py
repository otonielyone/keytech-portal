from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker
import os

DATABASE_PATH = "/var/www/html/keytech/database/inventory.db"
os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
sessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Inventory(Base):
    __tablename__ = "inventory"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    used = Column(Integer, default=0)

class InventoryHistory(Base):
    __tablename__ = "inventory_history"
    id = Column(Integer, primary_key=True, index=True)
    item = Column(String(100), nullable=False)
    change = Column(Integer, nullable=False)
    timestamp = Column(String(100), nullable=False)

def create_database():
    Base.metadata.create_all(bind=engine)
    print("Created Inventory Database!")
create_database()


def init_db():
    db = sessionLocal()
    try:
        for name in ["GPS Units", "Card Readers"]:
            if not db.query(Inventory).filter_by(name=name).first():
                db.add(Inventory(name=name, used=0))
        db.commit()
    finally:
        db.close()
init_db()