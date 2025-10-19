import sqlite3
import os
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Random import get_random_bytes
import json
import base64


class UserDatabase:
    """Encrypted SQLite database for storing single user data"""
    
    def __init__(self, db_name='user.db', password='your_password_here'):
        self.db_name = db_name
        self.encrypted_name = db_name + '.enc'
        self.password = password
        self.salt_file = db_name + '.salt'
        self.conn = None
    
    def __enter__(self):
        """Decrypt and open database"""
        self._decrypt_database()
        self.conn = sqlite3.connect(self.db_name)
        return self.conn
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Close and encrypt database"""
        if self.conn:
            self.conn.close()
        self._encrypt_database()
    
    def _get_key(self):
        """Generate or retrieve encryption key from password"""
        if os.path.exists(self.salt_file):
            with open(self.salt_file, 'rb') as f:
                salt = f.read()
        else:
            salt = get_random_bytes(32)
            with open(self.salt_file, 'wb') as f:
                f.write(salt)
        return PBKDF2(self.password, salt, dkLen=32)
    
    def _encrypt_field(self, data):
        """Encrypt a single field using AES-GCM"""
        if data is None:
            return None
        
        key = self._get_key()
        plaintext = str(data).encode('utf-8')
        
        cipher = AES.new(key, AES.MODE_GCM)
        ciphertext, tag = cipher.encrypt_and_digest(plaintext)
        
        # Combine nonce + tag + ciphertext and encode as base64
        encrypted_data = cipher.nonce + tag + ciphertext
        return base64.b64encode(encrypted_data).decode('utf-8')
    
    def _decrypt_field(self, encrypted_data):
        """Decrypt a single field"""
        if encrypted_data is None:
            return None
        
        try:
            key = self._get_key()
            encrypted_bytes = base64.b64decode(encrypted_data)
            
            # Extract components
            nonce = encrypted_bytes[:16]
            tag = encrypted_bytes[16:32]
            ciphertext = encrypted_bytes[32:]
            
            cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
            plaintext = cipher.decrypt_and_verify(ciphertext, tag)
            
            return plaintext.decode('utf-8')
        except Exception as e:
            print(f"Decryption error: {e}")
            return None
    
    def _encrypt_database(self):
        """Encrypt the entire database file"""
        if not os.path.exists(self.db_name):
            return
        
        key = self._get_key()
        
        with open(self.db_name, 'rb') as f:
            plaintext = f.read()
        
        cipher = AES.new(key, AES.MODE_GCM)
        ciphertext, tag = cipher.encrypt_and_digest(plaintext)
        
        encrypted_data = {
            'nonce': cipher.nonce.hex(),
            'tag': tag.hex(),
            'ciphertext': ciphertext.hex()
        }
        
        with open(self.encrypted_name, 'w') as f:
            json.dump(encrypted_data, f)
        
        os.remove(self.db_name)
    
    def _decrypt_database(self):
        """Decrypt the database file"""
        if not os.path.exists(self.encrypted_name):
            return
        
        key = self._get_key()
        
        with open(self.encrypted_name, 'r') as f:
            encrypted_data = json.load(f)
        
        cipher = AES.new(key, AES.MODE_GCM, 
                        nonce=bytes.fromhex(encrypted_data['nonce']))
        
        plaintext = cipher.decrypt_and_verify(
            bytes.fromhex(encrypted_data['ciphertext']),
            bytes.fromhex(encrypted_data['tag'])
        )
        
        with open(self.db_name, 'wb') as f:
            f.write(plaintext)
    
    def _create_table(self):
        """Create users table if it doesn't exist"""
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                age TEXT,
                city TEXT,
                income TEXT,
                expenses TEXT,
                shouldPayDebt TEXT,
                totalDebt TEXT,
                totalAmountInAccount TEXT,
                employment TEXT,
                netIncome TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()
    
    def create_table(self):
        """Public method to ensure table exists"""
        with self as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    age TEXT,
                    city TEXT,
                    income TEXT,
                    expenses TEXT,
                    shouldPayDebt TEXT,
                    totalDebt TEXT,
                    totalAmountInAccount TEXT,
                    employment TEXT,
                    netIncome TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
    
    def save_user(self, user_json):
        """
        Save user data from JSON (from frontend)
        
        Args:
            user_json: JSON string or dict containing user data
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Parse JSON if it's a string
            if isinstance(user_json, str):
                user_data = json.loads(user_json)
            else:
                user_data = user_json
            
            # Ensure table exists first
            self.create_table()
            
            with self as conn:
                cursor = conn.cursor()
                
                # Extract fields
                name = user_data.get('name')
                
                # Encrypt all sensitive fields
                encrypted_data = {
                    'age': self._encrypt_field(user_data.get('age')),
                    'city': self._encrypt_field(user_data.get('city')),
                    'income': self._encrypt_field(user_data.get('income')),
                    'expenses': self._encrypt_field(user_data.get('expenses')),
                    'shouldPayDebt': self._encrypt_field(user_data.get('shouldPayDebt')),
                    'totalDebt': self._encrypt_field(user_data.get('totalDebt')),
                    'totalAmountInAccount': self._encrypt_field(user_data.get('totalAmountInAccount')),
                    'employment': self._encrypt_field(user_data.get('employment')),
                    'netIncome': self._encrypt_field(user_data.get('netIncome'))
                }
                
                # Insert into database
                cursor.execute('''
                    INSERT INTO users (name, age, city, income, expenses, shouldPayDebt, 
                                     totalDebt, totalAmountInAccount, employment, netIncome)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (name, encrypted_data['age'], encrypted_data['city'], 
                      encrypted_data['income'], encrypted_data['expenses'],
                      encrypted_data['shouldPayDebt'], encrypted_data['totalDebt'],
                      encrypted_data['totalAmountInAccount'], encrypted_data['employment'],
                      encrypted_data['netIncome']))
                
                conn.commit()
                print(f"✅ User '{name}' saved and encrypted successfully")
                return True
                
        except Exception as e:
            print(f"❌ Error saving user: {e}")
            return False
    
    def get_user(self, name):
        """
        Retrieve and decrypt user data by name
        
        Args:
            name: Name of the user to retrieve
            
        Returns:
            Dictionary with decrypted user data, or None if not found
        """
        try:
            with self as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, name, age, city, income, expenses, shouldPayDebt, 
                           totalDebt, totalAmountInAccount, employment, netIncome, created_at 
                    FROM users WHERE name = ?
                ''', (name,))
                row = cursor.fetchone()
                
                if not row:
                    print(f"❌ User '{name}' not found")
                    return None
                
                # Decrypt and return user data
                user = {
                    'id': row[0],
                    'name': row[1],
                    'age': self._decrypt_field(row[2]),
                    'city': self._decrypt_field(row[3]),
                    'income': self._decrypt_field(row[4]),
                    'expenses': self._decrypt_field(row[5]),
                    'shouldPayDebt': self._decrypt_field(row[6]),
                    'totalDebt': self._decrypt_field(row[7]),
                    'totalAmountInAccount': self._decrypt_field(row[8]),
                    'employment': self._decrypt_field(row[9]),
                    'netIncome': self._decrypt_field(row[10]),
                    'created_at': row[11]
                }
                
                print(f"✅ User '{name}' retrieved and decrypted")
                return user
                
        except Exception as e:
            print(f"❌ Error retrieving user: {e}")
            return None


# Example usage
if __name__ == "__main__":
    # Initialize database with password
    db = UserDatabase(db_name='user.db', password='my_super_secret_password')
    
    # IMPORTANT: Create table first (only needed once, but safe to call multiple times)
    db.create_table()
    
    # Example 1: Save user from JSON (simulating frontend data)
    print("=" * 60)
    print("SAVING USER FROM FRONTEND JSON")
    print("=" * 60)
    
    frontend_json = {
        "name": "John Doe",
        "age": "30",
        "city": "New York",
        "income": "75000",
        "expenses": "45000",
        "shouldPayDebt": "yes",
        "totalDebt": "15000",
        "totalAmountInAccount": "10000",
        "employment": "Software Engineer",
        "netIncome": "30000"
    }
    
    db.save_user(frontend_json)
    
    # Example 2: Retrieve user data
    print("\n" + "=" * 60)
    print("RETRIEVING USER DATA")
    print("=" * 60)
    
    user_data = db.get_user('John Doe')
    if user_data:
        print(json.dumps(user_data, indent=2))