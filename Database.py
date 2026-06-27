"""
Handles all MySQL database operations for Nagar Seva
"""

import mysql.connector
from mysql.connector import Error
import datetime

class Database:
    #Handle all database operations
    
    def __init__(self, host='localhost', database='nagar_seva', user='root', password=''):
        self.connection = None
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.connect()
    
    def connect(self):
        #Connect to MySQL database
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password
            )
            print("✅ Connected to MySQL database!")
        except Error as e:
            print(f"❌ Error connecting to MySQL: {e}")
            print("\n💡 Please make sure:")
            print("   1. MySQL is running")
            print("   2. Database exists")
            print("   3. Username and password are correct")
            exit()
    
    def execute_query(self, query, params=None):
        #Execute a query and return results
        cursor = self.connection.cursor(dictionary=True)
        try:
            cursor.execute(query, params)
            if query.strip().upper().startswith('SELECT'):
                results = cursor.fetchall()
                cursor.close()
                return results
            else:
                self.connection.commit()
                cursor.close()
                return True
        except Error as e:
            print(f"❌ Database error: {e}")
            cursor.close()
            return None
    
    def execute_insert(self, query, params=None):
        #Execute an INSERT query and return the last inserted ID
        cursor = self.connection.cursor()
        try:
            cursor.execute(query, params)
            self.connection.commit()
            last_id = cursor.lastrowid
            cursor.close()
            return last_id
        except Error as e:
            print(f"❌ Database error: {e}")
            cursor.close()
            return None
    
    def close(self):
        #Close database connection
        if self.connection:
            self.connection.close()
            print("✅ Database connection closed")


class UserDB:
    #User-related database operations
    
    def __init__(self, db):
        self.db = db
    
    def create_user(self, name, mobile, ward, city):
        #Create a new user
        query = """
            INSERT INTO users (mobile, name, ward, city, points)
            VALUES (%s, %s, %s, %s, 0)
        """
        return self.db.execute_insert(query, (mobile, name, ward, city))
    
    def get_user_by_mobile(self, mobile):
        #Get user by mobile number
        query = "SELECT * FROM users WHERE mobile = %s"
        result = self.db.execute_query(query, (mobile,))
        return result[0] if result else None
    
    def update_user_points(self, mobile, points_to_add):
        #Update user points
        query = "UPDATE users SET points = points + %s WHERE mobile = %s"
        return self.db.execute_query(query, (points_to_add, mobile))
    
    def get_leaderboard(self, limit=10):
        #Get top users by points
        query = """
            SELECT name, mobile, points, ward, city 
            FROM users 
            ORDER BY points DESC 
            LIMIT %s
        """
        return self.db.execute_query(query, (limit,))
    
    def get_all_users(self):
        #Get all users
        query = "SELECT * FROM users ORDER BY name"
        return self.db.execute_query(query)


class GrievanceDB:
    #Grievance-related database operations
    
    def __init__(self, db):
        self.db = db
    
    def generate_grievance_id(self):
        #Generate a unique grievance ID
        year = datetime.datetime.now().year
        query = "SELECT COUNT(*) as count FROM grievances WHERE id LIKE %s"
        result = self.db.execute_query(query, (f"MCG-{year}-%",))
        
        if result and result[0]['count']:
            count = result[0]['count'] + 1
        else:
            count = 1
        
        return f"MCG-{year}-{str(count).zfill(6)}"
    
    def create_grievance(self, grievance_id, mobile, name, category, description, location):
        #Create a new grievance
        query = """
            INSERT INTO grievances (id, mobile, name, category, description, location)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        params = (grievance_id, mobile, name, category, description, location)
        return self.db.execute_insert(query, params)
    
    def get_grievance_by_id(self, grievance_id):
        #Get grievance by ID
        query = "SELECT * FROM grievances WHERE id = %s"
        result = self.db.execute_query(query, (grievance_id,))
        return result[0] if result else None
    
    def get_grievances_by_mobile(self, mobile):
        #Get all grievances for a user
        query = "SELECT * FROM grievances WHERE mobile = %s ORDER BY created_at DESC"
        return self.db.execute_query(query, (mobile,))
    
    def get_all_grievances(self):
        #Get all grievances
        query = "SELECT * FROM grievances ORDER BY created_at DESC"
        return self.db.execute_query(query)
    
    def update_grievance_status(self, grievance_id, new_status):
        #Update grievance status
        query = "UPDATE grievances SET status = %s WHERE id = %s"
        return self.db.execute_query(query, (new_status, grievance_id))
    
    def add_upvote(self, grievance_id):
        #Increment upvote count
        query = "UPDATE grievances SET upvotes = upvotes + 1 WHERE id = %s"
        return self.db.execute_query(query, (grievance_id,))
    
    def search_grievances(self, search_term):
        #Search grievances by description or location
        query = """
            SELECT * FROM grievances 
            WHERE description LIKE %s OR location LIKE %s
            ORDER BY created_at DESC
        """
        search_pattern = f"%{search_term}%"
        return self.db.execute_query(query, (search_pattern, search_pattern))
    
    def get_stats(self):
        #Get grievance statistics
        total_query = "SELECT COUNT(*) as total FROM grievances"
        total = self.db.execute_query(total_query)[0]['total']
        
        resolved_query = "SELECT COUNT(*) as resolved FROM grievances WHERE status = 'Resolved'"
        resolved = self.db.execute_query(resolved_query)[0]['resolved']
        
        pending = total - resolved
        
        category_query = """
            SELECT category, COUNT(*) as count 
            FROM grievances 
            GROUP BY category
        """
        categories = self.db.execute_query(category_query)
        
        status_query = """
            SELECT status, COUNT(*) as count 
            FROM grievances 
            GROUP BY status
        """
        statuses = self.db.execute_query(status_query)
        
        return {
            'total': total,
            'resolved': resolved,
            'pending': pending,
            'by_category': categories,
            'by_status': statuses
        }


class HistoryDB:
    #Status history database operations
    
    def __init__(self, db):
        self.db = db
    
    def add_history(self, grievance_id, status, remark):
        #Add status history entry
        query = """
            INSERT INTO status_history (grievance_id, status, remark)
            VALUES (%s, %s, %s)
        """
        return self.db.execute_insert(query, (grievance_id, status, remark))
    
    def get_history(self, grievance_id):
        #Get status history for a grievance
        query = """
            SELECT status, remark, updated_at 
            FROM status_history 
            WHERE grievance_id = %s 
            ORDER BY updated_at DESC
        """
        return self.db.execute_query(query, (grievance_id,))


class UpvoteDB:
    #Upvote database operations
    
    def __init__(self, db):
        self.db = db
    
    def has_upvoted(self, grievance_id, mobile):
        #Check if user already upvoted
        query = "SELECT * FROM upvotes WHERE grievance_id = %s AND mobile = %s"
        result = self.db.execute_query(query, (grievance_id, mobile))
        return bool(result)
    
    def add_upvote(self, grievance_id, mobile):
        #Add an upvote
        query = "INSERT INTO upvotes (grievance_id, mobile) VALUES (%s, %s)"
        return self.db.execute_insert(query, (grievance_id, mobile))