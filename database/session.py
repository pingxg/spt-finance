from contextlib import contextmanager
from sqlalchemy.exc import SQLAlchemyError
from database.models import SessionLocal

@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        print(f"Session rollback due to exception: {e}")
        raise
    except Exception as e:
        # Log non-SQLAlchemy exceptions if necessary
        print(f"An unexpected error occurred: {e}")
        raise
    finally:
        session.close()
