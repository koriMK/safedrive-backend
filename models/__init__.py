from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .user import User
from .driver import Driver
from .trip import Trip
from .payment import Payment
from .config import Config

__all__ = ['db', 'User', 'Driver', 'Trip', 'Payment', 'Config']