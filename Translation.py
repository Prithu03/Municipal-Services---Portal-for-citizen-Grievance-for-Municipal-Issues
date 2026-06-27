"""
Lightweight bilingual support (English / Hindi) for core UI strings.
Structured so additional regional languages (Marathi, Tamil, Bengali, etc.)
can be added later by extending the TRANSLATIONS dict.
"""
TRANSLATIONS = {
    "en": {
        "app_title": "Municipal Services — Citizen Grievance Portal",
        "tagline": "Report it. Track it. Build a cleaner, more systematic India — one ward at a time.",
        "nav_home": "🏠 Home",
        "nav_report": "📝 Report a Grievance",
        "nav_track": "🔍 Track My Grievance",
        "nav_map": "🗺️ Community Map & Issues",
        "nav_leaderboard": "🏆 Swachh Ward Leaderboard",
        "nav_awareness": "📅 Awareness Corner",
        "nav_admin": "🔐 Municipal Admin Panel",
        "login_name": "Your Name",
        "login_mobile": "Mobile Number (10 digit)",
        "login_ward": "Ward / Locality",
        "login_city": "City",
        "login_button": "Continue",
        "welcome": "Welcome",
        "total_reported": "Total Reported",
        "total_resolved": "Resolved",
        "total_pending": "Pending",
        "category": "Category",
        "description": "Describe the issue",
        "location_method": "How would you like to add the location?",
        "submit": "Submit Grievance",
        "status": "Status",
        "your_points": "Swachh Citizen Points",
    },
    "hi": {
        "app_title": "नगर सेवा — नागरिक शिकायत पोर्टल",
        "tagline": "शिकायत दर्ज करें। स्थिति देखें। एक साफ़ और व्यवस्थित भारत बनाएं — एक वार्ड से शुरुआत।",
        "nav_home": "🏠 होम",
        "nav_report": "📝 शिकायत दर्ज करें",
        "nav_track": "🔍 मेरी शिकायत ट्रैक करें",
        "nav_map": "🗺️ सामुदायिक मानचित्र व समस्याएँ",
        "nav_leaderboard": "🏆 स्वच्छ वार्ड लीडरबोर्ड",
        "nav_awareness": "📅 जागरूकता कॉर्नर",
        "nav_admin": "🔐 नगर निगम एडमिन पैनल",
        "login_name": "आपका नाम",
        "login_mobile": "मोबाइल नंबर (10 अंक)",
        "login_ward": "वार्ड / मोहल्ला",
        "login_city": "शहर",
        "login_button": "आगे बढ़ें",
        "welcome": "नमस्ते / स्वागत है",
        "total_reported": "कुल शिकायतें",
        "total_resolved": "सुलझी हुई",
        "total_pending": "लंबित",
        "category": "श्रेणी",
        "description": "समस्या का विवरण दें",
        "location_method": "आप स्थान कैसे जोड़ना चाहेंगे?",
        "submit": "शिकायत दर्ज करें",
        "status": "स्थिति",
        "your_points": "स्वच्छ नागरिक अंक",
    },
}


def t(key, lang="en"):
    """Translate a key; falls back to English, then to the key itself."""
    return TRANSLATIONS.get(lang, {}).get(key) or TRANSLATIONS["en"].get(key, key)
