from . import db
from datetime import datetime
import uuid

class Config(db.Model):
    __tablename__ = 'config'
    
    id = db.Column(db.String(50), primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text, nullable=False)
    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, key, value, description=None):
        self.id = f'cfg_{uuid.uuid4().hex[:12]}'
        self.key = key
        self.value = value
        self.description = description
    
    @staticmethod
    def get_value(key, default=None):
        try:
            config = Config.query.filter_by(key=key).first()
            return config.value if config else default
        except:
            return default
    
    @staticmethod
    def set_value(key, value, description=None):
        config = Config.query.filter_by(key=key).first()
        if config:
            config.value = value
            config.updated_at = datetime.utcnow()
        else:
            config = Config(key=key, value=value, description=description)
            db.session.add(config)
        db.session.commit()
        return config