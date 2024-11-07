import time
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from forecasting import create_app 
from forecasting.models import db

app = create_app()

def check_database_health(engine, max_retries=5, retry_delay=1):
    """Checks if the database is healthy and ready to accept connections."""
    for attempt in range(max_retries):
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True  
        except OperationalError:
            if attempt < max_retries - 1:  
                time.sleep(retry_delay)
            else:
                return False

with app.app_context():
    engine = db.engine

    if not check_database_health(engine):
        raise Exception("Database connection failed. Unable to initialize the database.")

    db.create_all()