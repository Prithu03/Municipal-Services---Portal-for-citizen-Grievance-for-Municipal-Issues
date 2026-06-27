"""
Utility functions, constants, and configuration for Municipal service
"""

import datetime
import re

# CONSTANTS

# Category mapping
CATEGORIES = {
    '1': 'Garbage & Sanitation',
    '2': 'Roads & Footpaths',
    '3': 'Street Lighting',
    '4': 'Water Supply',
    '5': 'Sewage & Drainage',
    '6': 'Parks & Gardens',
    '7': 'Public Transport',
    '8': 'Encroachment',
    '9': 'Others'
}

# Status flow
STATUSES = ['Submitted', 'Acknowledged', 'In Progress', 'Resolved']

# Status icons for display
STATUS_ICONS = {
    'Submitted': '🟡',
    'Acknowledged': '🔵',
    'In Progress': '🟠',
    'Resolved': '🟢'
}

# Points system
POINTS_FOR_REPORT = 10
POINTS_FOR_UPVOTE = 2
POINTS_FOR_RESOLUTION = 15

# Demo credentials
DEMO_OTP = '123456'
ADMIN_PASSWORD = 'swachh2026'

# HELPER FUNCTIONS

def validate_mobile(mobile):
    """Validate Indian mobile number (10 digits)"""
    return mobile and len(mobile) == 10 and mobile.isdigit()

def validate_input(text):
    """Check if input is not empty"""
    return text and text.strip()

def get_current_timestamp():
    """Get current timestamp as string"""
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_current_date():
    """Get current date as string"""
    return datetime.datetime.now().strftime("%Y-%m-%d")

def display_status_icon(status):
    """Get status icon for display"""
    return STATUS_ICONS.get(status, '⚪')

def display_medal(position):
    """Get medal emoji for leaderboard position"""
    medals = ['🥇', '🥈', '🥉']
    return medals[position] if position < 3 else f"{position + 1}."

def parse_grievance_id(text):
    """Extract and clean grievance ID from text"""
    if not text:
        return None
    # Remove whitespace and convert to uppercase
    return text.strip().upper()

def get_upcoming_festival():
    """Get upcoming festival information"""
    festivals = [
        {"date": "2026-01-26", "name": "Republic Day", "tip": "Celebrate responsibly"},
        {"date": "2026-03-04", "name": "Holi", "tip": "Use natural colors"},
        {"date": "2026-08-15", "name": "Independence Day", "tip": "Keep public spaces clean"},
        {"date": "2026-11-12", "name": "Diwali", "tip": "Use eco-friendly crackers"}
    ]
    
    today = datetime.datetime.now().date()
    
    for festival in festivals:
        f_date = datetime.datetime.strptime(festival['date'], "%Y-%m-%d").date()
        days_until = (f_date - today).days
        if 0 <= days_until <= 10:
            return festival
    
    return None

def get_emergency_numbers():
    """Get emergency contact numbers"""
    return {
        "🚨 National Emergency": "112",
        "👮 Police": "100",
        "🚑 Ambulance": "108",
        "🚒 Fire": "101",
        "👩 Women's Helpline": "1091",
        "🧒 Child Helpline": "1098"
    }

def get_waste_segregation_guide():
    """Get waste segregation guide"""
    return {
        "🟢 Wet Waste": "Food scraps, peels, garden waste - goes in green bin",
        "🔵 Dry Waste": "Paper, plastic, glass - goes in blue bin",
        "🔴 Hazardous": "Batteries, e-waste - special disposal required"
    }

def print_header(title):
    """Print a formatted header"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def print_subheader(text):
    """Print a formatted subheader"""
    print("-"*40)
    print(text)
    print("-"*40)

def get_user_choice(prompt, options):
    """Get and validate user choice from a list of options"""
    while True:
        choice = input(prompt).strip()
        if choice in options:
            return choice
        print(f"❌ Invalid choice! Please choose from: {', '.join(options)}")

def format_grievance_summary(grievance):
    """Format a grievance for display"""
    icon = display_status_icon(grievance['status'])
    return f"📌 {grievance['id']} - {grievance['category']} ({icon} {grievance['status']})"

def format_user_summary(user):
    """Format a user for display"""
    return f"{user['name']} ({user['mobile']}) - Points: {user['points']}"

# VALIDATION CLASSES

class Validator:
    """Input validation helper"""
    
    @staticmethod
    def not_empty(text):
        """Check if text is not empty"""
        return bool(text and text.strip())
    
    @staticmethod
    def is_mobile(mobile):
        """Check if valid mobile number"""
        return validate_mobile(mobile)
    
    @staticmethod
    def is_valid_category(choice):
        """Check if valid category choice"""
        return choice in CATEGORIES
    
    @staticmethod
    def is_valid_status(status):
        """Check if valid status"""
        return status in STATUSES
    
    @staticmethod
    def is_valid_grievance_id(g_id):
        """Check if valid grievance ID format"""
        return bool(re.match(r'^MCG-\d{4}-\d{6}$', g_id))