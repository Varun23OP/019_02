from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from backend.config import settings

# Create database engine
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()


def get_db():
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db_schema():
    """Ensure newly added columns exist in SQLite database"""
    Base.metadata.create_all(bind=engine)
    with engine.connect() as conn:
        if "sqlite" in settings.DATABASE_URL:
            res = conn.exec_driver_sql("PRAGMA table_info(farmers)").fetchall()
            col_names = [r[1] for r in res]
            if "fpo_name" not in col_names:
                conn.exec_driver_sql("ALTER TABLE farmers ADD COLUMN fpo_name VARCHAR(255)")
                conn.commit()
