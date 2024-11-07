from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import validates
from sqlalchemy import text
from sqlalchemy.sql import func
import uuid

db = SQLAlchemy()
