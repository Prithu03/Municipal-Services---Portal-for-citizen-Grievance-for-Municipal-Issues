"""
Main application logic for Nagar Seva
"""

import os
from database import Database, UserDB, GrievanceDB, HistoryDB, UpvoteDB
from utils import *
from translations import t, Translator

class MunicipalServicesApp:
    #Main application class
    
    def __init__(self):
        # Initialize database
        self.db = Database()
        
        # Initialize database handlers
        self.user_db = UserDB(self.db)
        self.grievance_db = GrievanceDB(self.db)
        self.history_db = HistoryDB(self.db)
        self.upvote_db = UpvoteDB(self.db)
        
        # Application state
        self.current_user = None
        self.translator = Translator('en')
        self.running = True
        
        # Display startup info
        self.print_startup_info()
    
    def print_startup_info(self):
        """Print startup information"""
        print("\n" + "="*60)
        print("  🇮🇳 NAGAR SEVA - Citizen Grievance Portal")
        print("  Your Voice for Better Cities")
        print("="*60)
        print(f"\n💡 Demo OTP: {DEMO_OTP}")
        print(f"💡 Admin Password: {ADMIN_PASSWORD}")
        print("\n📱 Make sure MySQL is running!")
        print("="*60)
    
    def clear_screen(self):
        """Clear the terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def t(self, key):
        """Translate a key"""
        return self.translator.get(key)
    
    def display_header(self):
        """Display application header"""
        print("\n" + "="*60)
        print(f"  🇮🇳 {self.t('app_name')}")
        print(f"  {self.t('app_subtitle')}")
        print("="*60)
    
    def display_user_info(self):
        """Display current user information"""
        if self.current_user:
            print(f"\n👋 {self.t('welcome')}, {self.current_user['name']}!")
            print(f"📱 {self.t('mobile')}: {self.current_user['mobile']}")
            print(f"🏆 {self.t('points')}: {self.current_user['points']}")
            print("-"*40)
    
    def display_menu(self):
        """Display main menu"""
        self.display_user_info()
        
        if self.current_user:
            print("\n📋 MAIN MENU:")
            print("  1. Report a Grievance")
            print("  2. View My Grievances")
            print("  3. Track Grievance by ID")
            print("  4. View All Grievances")
            print("  5. Upvote a Grievance")
            print("  6. Search Grievances")
            print("  7. View Leaderboard")
            print("  8. View Statistics")
            print("  9. Admin Panel")
            print("  0. Logout")
        else:
            print("\n📋 MAIN MENU:")
            print("  1. Register")
            print("  2. Login")
            print("  3. View All Grievances")
            print("  4. Search Grievances")
            print("  5. View Leaderboard")
            print("  6. View Statistics")
            print("  0. Exit")
    
    def get_choice(self):
        """Get user's menu choice"""
        try:
            choice = input("\n👉 Enter your choice: ").strip()
            return choice
        except KeyboardInterrupt:
            print("\n\n👋 Thank you for using Nagar Seva!")
            self.running = False
            return '0'
    
    # USER OPERATIONS
    
    def register_user(self):
        """Handle user registration"""
        self.clear_screen()
        print_header("📝 REGISTER NEW USER")
        
        name = input("Enter your name: ").strip()
        mobile = input("Enter mobile number (10 digits): ").strip()
        ward = input("Enter your ward/locality: ").strip()
        city = input("Enter your city: ").strip()
        
        # Validate input
        if not all([name, mobile, ward, city]):
            print("\n❌ All fields are required!")
            input("\nPress Enter to continue...")
            return
        
        if not validate_mobile(mobile):
            print("\n❌ Please enter a valid 10-digit mobile number!")
            input("\nPress Enter to continue...")
            return
        
        # Check if user exists
        existing_user = self.user_db.get_user_by_mobile(mobile)
        if existing_user:
            print("\n❌ User already exists!")
            input("\nPress Enter to continue...")
            return
        
        # Create user
        result = self.user_db.create_user(name, mobile, ward, city)
        
        if result:
            print(f"\n✅ Registration successful! Welcome {name}!")
        else:
            print("\n❌ Registration failed!")
        
        input("\nPress Enter to continue...")
    
    def login_user(self):
        """Handle user login"""
        self.clear_screen()
        print_header("🔐 LOGIN")
        
        mobile = input("Enter your mobile number: ").strip()
        
        if not validate_mobile(mobile):
            print("\n❌ Please enter a valid 10-digit mobile number!")
            input("\nPress Enter to continue...")
            return
        
        # Check if user exists
        user = self.user_db.get_user_by_mobile(mobile)
        if not user:
            print("\n❌ User not found! Please register first.")
            input("\nPress Enter to continue...")
            return
        
        print(f"\n📩 Demo OTP sent to {mobile}")
        otp = input("Enter OTP: ").strip()
        
        if otp == DEMO_OTP:
            self.current_user = user
            print(f"\n✅ Welcome back {user['name']}!")
        else:
            print("\n❌ Invalid OTP!")
        
        input("\nPress Enter to continue...")
    
    def logout_user(self):
        """Handle user logout"""
        self.current_user = None
        print("\n✅ Logged out successfully!")
        input("\nPress Enter to continue...")
    
    # GRIEVANCE OPERATIONS
    
    def report_grievance(self):
        """Handle reporting a new grievance"""
        if not self.current_user:
            print("\n❌ Please login first!")
            input("\nPress Enter to continue...")
            return
        
        self.clear_screen()
        print_header("📝 REPORT A GRIEVANCE")
        
        # Show categories
        print("\n📂 Select Category:")
        for key, value in CATEGORIES.items():
            print(f"  {key}. {value}")
        
        category_choice = input("\n👉 Choose category (1-9): ").strip()
        
        if not Validator.is_valid_category(category_choice):
            print("\n❌ Invalid category!")
            input("\nPress Enter to continue...")
            return
        
        description = input("\n📝 Describe the issue: ").strip()
        
        if not validate_input(description):
            print("\n❌ Description is required!")
            input("\nPress Enter to continue...")
            return
        
        location = input("\n📍 Location/Address: ").strip()
        
        if not validate_input(location):
            print("\n❌ Location is required!")
            input("\nPress Enter to continue...")
            return
        
        # Generate grievance ID
        grievance_id = self.grievance_db.generate_grievance_id()
        
        # Create grievance
        result = self.grievance_db.create_grievance(
            grievance_id,
            self.current_user['mobile'],
            self.current_user['name'],
            CATEGORIES[category_choice],
            description,
            location
        )
        
        if result:
            # Add status history
            self.history_db.add_history(grievance_id, 'Submitted', 'Grievance submitted')
            
            # Add points
            self.user_db.update_user_points(self.current_user['mobile'], POINTS_FOR_REPORT)
            self.current_user['points'] += POINTS_FOR_REPORT
            
            print(f"\n✅ Grievance Reported Successfully!")
            print(f"📋 Your Grievance ID: {grievance_id}")
            print(f"⭐ You earned {POINTS_FOR_REPORT} Swachh Citizen points!")
        else:
            print("\n❌ Failed to create grievance!")
        
        input("\nPress Enter to continue...")
    
    def view_my_grievances(self):
        """View user's own grievances"""
        if not self.current_user:
            print("\n❌ Please login first!")
            input("\nPress Enter to continue...")
            return
        
        self.clear_screen()
        print_header("🔍 MY GRIEVANCES")
        
        grievances = self.grievance_db.get_grievances_by_mobile(self.current_user['mobile'])
        
        if not grievances:
            print("\n📭 You haven't filed any grievances yet.")
            input("\nPress Enter to continue...")
            return
        
        print(f"\n📋 Your Grievances ({len(grievances)} total):\n")
        
        for i, g in enumerate(grievances, 1):
            icon = display_status_icon(g['status'])
            print(f"  {i}. {g['id']}")
            print(f"     Category: {g['category']}")
            print(f"     Status: {icon} {g['status']}")
            print(f"     Upvotes: 👍 {g['upvotes']}")
            print(f"     Date: {g['created_at']}")
            print("-"*40)
        
        # Option to view details
        choice = input("\n👉 Enter grievance number to view details (or 0 to cancel): ").strip()
        
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(grievances):
                self.display_grievance_details(grievances[idx]['id'])
        except ValueError:
            pass
    
    def display_grievance_details(self, grievance_id):
        """Display detailed grievance information"""
        self.clear_screen()
        print_header("📋 GRIEVANCE DETAILS")
        
        grievance = self.grievance_db.get_grievance_by_id(grievance_id)
        
        if not grievance:
            print("\n❌ Grievance not found!")
            input("\nPress Enter to continue...")
            return
        
        print(f"\nID: {grievance['id']}")
        print(f"Category: {grievance['category']}")
        print(f"Status: {display_status_icon(grievance['status'])} {grievance['status']}")
        print(f"Description: {grievance['description']}")
        print(f"Location: {grievance['location']}")
        print(f"Upvotes: 👍 {grievance['upvotes']}")
        print(f"Reported by: {grievance['name']}")
        print(f"Created: {grievance['created_at']}")
        
        # Show status history
        print("\n📊 Status History:")
        history = self.history_db.get_history(grievance_id)
        for h in history:
            print(f"  ⏰ {h['status']} - {h['remark']} ({h['updated_at']})")
        
        input("\nPress Enter to continue...")
    
    def track_grievance_by_id(self):
        """Track a grievance by ID"""
        self.clear_screen()
        print_header("🔍 TRACK GRIEVANCE BY ID")
        
        grievance_id = input("Enter Grievance ID (e.g., MCG-2026-000001): ").strip().upper()
        
        if not grievance_id:
            print("\n❌ Please enter a grievance ID!")
            input("\nPress Enter to continue...")
            return
        
        self.display_grievance_details(grievance_id)
    
    def view_all_grievances(self):
        """View all grievances"""
        self.clear_screen()
        print_header("📋 ALL GRIEVANCES")
        
        grievances = self.grievance_db.get_all_grievances()
        
        if not grievances:
            print("\n📭 No grievances found.")
            input("\nPress Enter to continue...")
            return
        
        print(f"\n📊 Total Grievances: {len(grievances)}\n")
        
        for g in grievances[:20]:
            icon = display_status_icon(g['status'])
            print(f"📌 {g['id']}")
            print(f"   Category: {g['category']}")
            print(f"   Status: {icon} {g['status']}")
            print(f"   Upvotes: 👍 {g['upvotes']}")
            print(f"   Reported by: {g['name']}")
            print("-"*40)
        
        if len(grievances) > 20:
            print(f"... and {len(grievances) - 20} more grievances")
        
        input("\nPress Enter to continue...")
    
    def upvote_grievance(self):
        """Upvote a grievance"""
        if not self.current_user:
            print("\n❌ Please login first!")
            input("\nPress Enter to continue...")
            return
        
        self.clear_screen()
        print_header("👍 UPVOTE A GRIEVANCE")
        
        grievance_id = input("Enter Grievance ID to upvote: ").strip().upper()
        
        if not grievance_id:
            print("\n❌ Please enter a grievance ID!")
            input("\nPress Enter to continue...")
            return
        
        # Check if grievance exists
        grievance = self.grievance_db.get_grievance_by_id(grievance_id)
        
        if not grievance:
            print("\n❌ Grievance not found!")
            input("\nPress Enter to continue...")
            return
        
        # Check if user is the reporter
        if grievance['mobile'] == self.current_user['mobile']:
            print("\n❌ You cannot upvote your own grievance!")
            input("\nPress Enter to continue...")
            return
        
        # Check if already upvoted
        if self.upvote_db.has_upvoted(grievance_id, self.current_user['mobile']):
            print("\n❌ You already upvoted this grievance!")
            input("\nPress Enter to continue...")
            return
        
        # Add upvote
        result = self.upvote_db.add_upvote(grievance_id, self.current_user['mobile'])
        
        if result:
            # Update grievance upvote count
            self.grievance_db.add_upvote(grievance_id)
            
            # Add points
            self.user_db.update_user_points(self.current_user['mobile'], POINTS_FOR_UPVOTE)
            self.current_user['points'] += POINTS_FOR_UPVOTE
            
            print(f"\n✅ Upvoted successfully!")
            print(f"⭐ You earned {POINTS_FOR_UPVOTE} points for upvoting!")
        else:
            print("\n❌ Failed to upvote!")
        
        input("\nPress Enter to continue...")
    
    def search_grievances(self):
        """Search grievances"""
        self.clear_screen()
        print_header("🔍 SEARCH GRIEVANCES")
        
        search_term = input("\nEnter search term (description or location): ").strip()
        
        if not search_term:
            print("\n❌ Please enter a search term!")
            input("\nPress Enter to continue...")
            return
        
        results = self.grievance_db.search_grievances(search_term)
        
        if not results:
            print(f"\n📭 No grievances found matching '{search_term}'")
        else:
            print(f"\n📋 Found {len(results)} grievances:\n")
            for g in results[:10]:
                icon = display_status_icon(g['status'])
                print(f"📌 {g['id']