from datetime import datetime
import re
import uuid
import math

def generate_id(prefix=''):
    """Generate unique ID with optional prefix"""
    unique_id = uuid.uuid4().hex[:12]
    return f'{prefix}_{unique_id}' if prefix else unique_id

def format_phone_number(phone):
    """Format phone number to Kenyan standard (+254...)"""
    # Remove all non-numeric characters
    phone = re.sub(r'\D', '', phone)
    
    # Handle different formats
    if phone.startswith('254'):
        return f'+{phone}'
    elif phone.startswith('0'):
        return f'+254{phone[1:]}'
    elif phone.startswith('7') or phone.startswith('1'):
        return f'+254{phone}'
    
    return phone

def validate_kenyan_phone(phone):
    """Validate Kenyan phone number"""
    formatted = format_phone_number(phone)
    pattern = r'^\+254[17]\d{8}$'
    return re.match(pattern, formatted) is not None

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two points using Haversine formula"""
    R = 6371  # Earth's radius in kilometers
    
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    
    a = (math.sin(dlat/2) ** 2 + 
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * 
         math.sin(dlon/2) ** 2)
    
    c = 2 * math.asin(math.sqrt(a))
    
    return R * c

def calculate_fare(distance_km):
    """Calculate trip fare based on distance"""
    BASE_FARE = 200  # KES
    RATE_PER_KM = 50  # KES per kilometer
    MINIMUM_FARE = 150  # KES
    
    fare = BASE_FARE + (distance_km * RATE_PER_KM)
    
    return max(MINIMUM_FARE, round(fare, 2))

def estimate_duration(distance_km, avg_speed_kmh=30):
    """Estimate trip duration in minutes"""
    hours = distance_km / avg_speed_kmh
    minutes = hours * 60
    return int(minutes)

def parse_date(date_string):
    """Parse date string to datetime object"""
    formats = [
        '%Y-%m-%d',
        '%Y-%m-%dT%H:%M:%S',
        '%Y-%m-%d %H:%M:%S',
        '%d/%m/%Y',
        '%m/%d/%Y'
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_string, fmt)
        except ValueError:
            continue
    
    raise ValueError(f'Unable to parse date: {date_string}')

def format_currency(amount):
    """Format amount as Kenyan Shillings"""
    return f'KES {amount:,.2f}'

def sanitize_input(text, max_length=None):
    """Sanitize user input"""
    if not text:
        return ''
    
    # Remove leading/trailing whitespace
    text = text.strip()
    
    # Remove any potentially harmful characters
    text = re.sub(r'[<>{}]', '', text)
    
    # Limit length if specified
    if max_length and len(text) > max_length:
        text = text[:max_length]
    
    return text

def is_valid_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def generate_otp(length=6):
    """Generate random OTP"""
    import random
    return ''.join([str(random.randint(0, 9)) for _ in range(length)])

def hash_file(filepath):
    """Generate hash for file (for document verification)"""
    import hashlib
    
    hasher = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hasher.update(chunk)
    
    return hasher.hexdigest()