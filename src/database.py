from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from src.config import settings

# Create database engine
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_recycle=300,
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Session:
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables."""
    # Import Base from models to ensure consistency
    from src.models import Base
    
    # Import all models to ensure they're registered with Base
    from src.models import Source, Content, Summary, User, UserSource, Alert, ScheduledTask
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Verify tables were created
    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"✅ Created tables: {', '.join(tables)}")


def close_db():
    """Close database connections."""
    engine.dispose()
