"""
Handles translations for multilingual support
"""

# Translation dictionaries
TRANSLATIONS = {
    'en': {
        'app_name': 'Nagar Seva',
        'app_subtitle': 'Your Voice for Better Cities',
        'welcome': 'Welcome',
        'login': 'Login',
        'register': 'Register',
        'logout': 'Logout',
        'report': 'Report a Grievance',
        'track': 'Track Grievance',
        'view_all': 'View All Grievances',
        'search': 'Search Grievances',
        'leaderboard': 'Leaderboard',
        'statistics': 'Statistics',
        'admin': 'Admin Panel',
        'exit': 'Exit',
        'name': 'Name',
        'mobile': 'Mobile Number',
        'ward': 'Ward/Locality',
        'city': 'City',
        'otp': 'OTP',
        'category': 'Category',
        'description': 'Description',
        'location': 'Location',
        'status': 'Status',
        'upvotes': 'Upvotes',
        'points': 'Points',
        'date': 'Date',
        'success': 'Success',
        'error': 'Error',
        'info': 'Information',
        'warning': 'Warning',
        'yes': 'Yes',
        'no': 'No',
        'cancel': 'Cancel',
        'confirm': 'Confirm',
        'required': 'This field is required',
        'invalid': 'Invalid input',
        'not_found': 'Not found',
        'already_exists': 'Already exists',
        'no_data': 'No data available',
        'loading': 'Loading...',
        'processing': 'Processing...'
    },
    'hi': {
        'app_name': 'नगर सेवा',
        'app_subtitle': 'बेहतर शहरों के लिए आपकी आवाज',
        'welcome': 'स्वागत है',
        'login': 'लॉगिन',
        'register': 'पंजीकरण',
        'logout': 'लॉगआउट',
        'report': 'शिकायत दर्ज करें',
        'track': 'शिकायत ट्रैक करें',
        'view_all': 'सभी शिकायतें देखें',
        'search': 'शिकायत खोजें',
        'leaderboard': 'लीडरबोर्ड',
        'statistics': 'आंकड़े',
        'admin': 'प्रशासक पैनल',
        'exit': 'बाहर जाएं',
        'name': 'नाम',
        'mobile': 'मोबाइल नंबर',
        'ward': 'वार्ड/इलाका',
        'city': 'शहर',
        'otp': 'ओटीपी',
        'category': 'श्रेणी',
        'description': 'विवरण',
        'location': 'स्थान',
        'status': 'स्थिति',
        'upvotes': 'समर्थन',
        'points': 'अंक',
        'date': 'तारीख',
        'success': 'सफलता',
        'error': 'त्रुटि',
        'info': 'जानकारी',
        'warning': 'चेतावनी',
        'yes': 'हाँ',
        'no': 'नहीं',
        'cancel': 'रद्द करें',
        'confirm': 'पुष्टि करें',
        'required': 'यह फ़ील्ड आवश्यक है',
        'invalid': 'अमान्य इनपुट',
        'not_found': 'नहीं मिला',
        'already_exists': 'पहले से मौजूद है',
        'no_data': 'कोई डेटा उपलब्ध नहीं',
        'loading': 'लोड हो रहा है...',
        'processing': 'प्रक्रिया हो रही है...'
    }
}

# Default language
DEFAULT_LANGUAGE = 'en'

class Translator:
    """Handle translations"""
    
    def __init__(self, language='en'):
        self.language = language
    
    def set_language(self, language):
        """Set current language"""
        if language in TRANSLATIONS:
            self.language = language
            return True
        return False
    
    def get(self, key):
        """Get translated text for a key"""
        # Get translation for current language
        if self.language in TRANSLATIONS and key in TRANSLATIONS[self.language]:
            return TRANSLATIONS[self.language][key]
        
        # Fallback to English
        if key in TRANSLATIONS['en']:
            return TRANSLATIONS['en'][key]
        
        # Return the key itself if not found
        return key
    
    def get_all_languages(self):
        """Get list of available languages"""
        return list(TRANSLATIONS.keys())
    
    def get_language_name(self, lang_code):
        """Get display name for language code"""
        names = {
            'en': 'English',
            'hi': 'हिंदी'
        }
        return names.get(lang_code, lang_code)

# Create a default translator instance
default_translator = Translator()

# Helper function for quick translation
def t(key, lang='en'):
    """Quick translation function"""
    translator = Translator(lang)
    return translator.get(key)