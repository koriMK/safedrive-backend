from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .user import User
from .driver import Driver
from .trip import Trip
from .payment import Payment
from .config import Config
from .notification import Notification
from .rating import Rating

__all__ = ['db', 'User', 'Driver', 'Trip', 'Payment', 'Config', 'Notification', 'Rating']