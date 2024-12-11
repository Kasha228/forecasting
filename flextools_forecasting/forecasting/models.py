from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import validates
from sqlalchemy import text
from sqlalchemy.sql import func
import uuid

db = SQLAlchemy()

class BaseForecast(db.Model):
    __abstract__ = True
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=text("gen_random_uuid()"))
    timestamp = db.Column(db.DateTime(timezone=True), server_default=func.now())
    input_data = db.Column(db.JSON)
    algorithm = db.Column(db.String(255), nullable=False)
    predicted_output = db.Column(db.JSON, nullable=False)

    def __repr__(self):
        return f"BaseForecast(id={self.id}, timestamp={self.timestamp}, input_data={self.input_data}, algorithm={self.algorithm}, predicted_output={self.predicted_output})"

    def to_dict(self):
        return {
            'id': str(self.id),
            'timestamp': self.timestamp.isoformat(),
            'input_data': self.input_data,
            'algorithm': self.algorithm,
            'predicted_output': self.predicted_output
        }

    @validates('id')
    def validate_id(self, key, value):
        if self.id and self.id != value: 
            raise ValueError("Cannot change the id of a BaseForecast")
        return value

    @validates('timestamp')
    def validate_timestamp(self, key, value):
        if self.timestamp and self.timestamp != value: 
            raise ValueError("Cannot change the timestamp of a BaseForecast")
        return value
    
    @validates('algorithm')
    def validate_algorithm(self, key, value):
        if not value: 
            raise ValueError("algorithm cannot be empty")
        return value

class TransactionForecast(BaseForecast):
    __tablename__ = 'transaction_forecast'
    event_type = db.Column(db.String(255), nullable=False)

    def to_dict(self):
        data = super().to_dict()
        data['event_type'] = self.event_type
        return data

    @validates('event_type')
    def validate_event_type(self, key, value):
        if not value: 
            raise ValueError("event_type cannot be empty")
        return value