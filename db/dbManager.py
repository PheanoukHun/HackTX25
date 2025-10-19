import sqlite3
import os
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Random import get_random_bytes
import json
import base64
import bcrypt


def encrypt_password(password):
    """Hashes a password using bcrypt."""
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed.decode('utf-8')

def check_password(password, hashed_password):
    """Checks if a plaintext password matches a hashed password."""
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))


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
        
        # Try to remove the plaintext file, with retry logic
        try:
            os.remove(self.db_name)
        except PermissionError:
            # File is still locked, try closing any remaining connections
            import time
            time.sleep(0.1)  # Brief delay
            try:
                os.remove(self.db_name)
            except Exception:
                pass  # If still locked, it will be overwritten on next decrypt
    
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
        
        # Remove existing plaintext file if it exists
        if os.path.exists(self.db_name):
            try:
                os.remove(self.db_name)
            except PermissionError:
                pass  # Will be overwritten anyway
        
        with open(self.db_name, 'wb') as f:
            f.write(plaintext)
    
    def create_table(self):
        """Public method to ensure table exists"""
        with self as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    password_hash TEXT,
                    age TEXT,
                    city TEXT,
                    employment TEXT,
                    housing_situation TEXT,
                    dining_habits TEXT,
                    monthly_subscriptions TEXT,
                    income TEXT,
                    expenses TEXT,
                    totalDebt TEXT,
                    credit_score TEXT,
                    totalAmountInAccount TEXT,
                    financial_goal TEXT,
                    financial_confidence_score TEXT,
                    netIncome TEXT,
                    context TEXT
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
                password_hash = user_data.get('password_hash') # Expecting hashed password from app.py
                
                # Encrypt all sensitive fields
                encrypted_data = {
                    'age': self._encrypt_field(user_data.get('age')),
                    'city': self._encrypt_field(user_data.get('location')), # Map 'location' from frontend to 'city' in DB
                    'income': self._encrypt_field(user_data.get('monthly_income')),
                    'expenses': self._encrypt_field(user_data.get('monthly_expenses')),
                    'totalDebt': self._encrypt_field(user_data.get('total_debt')),
                    'totalAmountInAccount': self._encrypt_field(user_data.get('bank_account_balance')),
                    'employment': self._encrypt_field(user_data.get('employment_status')),
                    'netIncome': self._encrypt_field(user_data.get('monthly_income') - user_data.get('monthly_expenses') if user_data.get('monthly_income') is not None and user_data.get('monthly_expenses') is not None else None),
                    'context': self._encrypt_field(user_data.get('past_conversation_context')),
                    'housing_situation': self._encrypt_field(user_data.get('housing_situation')),
                    'dining_habits': self._encrypt_field(user_data.get('dining_habits')),
                    'monthly_subscriptions': self._encrypt_field(user_data.get('monthly_subscriptions')),
                    'credit_score': self._encrypt_field(user_data.get('credit_score')),
                    'financial_goal': self._encrypt_field(user_data.get('financial_goal')),
                    'financial_confidence_score': self._encrypt_field(user_data.get('financial_confidence_score'))
                }
                
                # Insert into database
                cursor.execute('''
                    INSERT INTO users (name, password_hash, age, city, income, expenses,
                                     totalDebt, totalAmountInAccount, employment, netIncome, context)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (name, password_hash, encrypted_data['age'], encrypted_data['city'],
                      encrypted_data['income'], encrypted_data['expenses'], encrypted_data['totalDebt'],
                      encrypted_data['totalAmountInAccount'], encrypted_data['employment'],
                      encrypted_data['netIncome'], encrypted_data['context']))
                
                conn.commit()
                print(f"User '{name}' saved and encrypted successfully")
                return True
                
        except Exception as e:
            print(f"Error saving user: {e}")
            return False
    
    def update_user(self, name, updated_data):
        """
        Update existing user data
        
        Args:
            name: Name of the user to update
            updated_data: Dictionary with fields to update
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with self as conn:
                cursor = conn.cursor()
                
                # Check if user exists
                cursor.execute('SELECT id FROM users WHERE name = ?', (name,))
                if not cursor.fetchone():
                    print(f"User '{name}' not found")
                    return False
                
                # Build update query dynamically based on provided fields
                update_fields = []
                update_values = []
                
                # Encrypt each field that's being updated
                field_map = {
                    'age': 'age',
                    'location': 'city', # Map 'location' from frontend to 'city' in DB
                    'monthly_income': 'income',
                    'monthly_expenses': 'expenses',
                    'total_debt': 'totalDebt',
                    'bank_account_balance': 'totalAmountInAccount',
                    'employment_status': 'employment',
                    'past_conversation_context': 'context',
                    'housing_situation': 'housing_situation',
                    'dining_habits': 'dining_habits',
                    'monthly_subscriptions': 'monthly_subscriptions',
                    'credit_score': 'credit_score',
                    'financial_goal': 'financial_goal',
                    'financial_confidence_score': 'financial_confidence_score'
                }
                
                for field, column in field_map.items():
                    if field in updated_data:
                        update_fields.append(f"{column} = ?")
                        update_values.append(self._encrypt_field(updated_data[field]))
                
                # Handle password hash separately
                if 'password_hash' in updated_data:
                    update_fields.append("password_hash = ?")
                    update_values.append(updated_data['password_hash']) # Already hashed
                
                if not update_fields:
                    print("No valid fields to update")
                    return False
                
                # Add name to the end for WHERE clause
                update_values.append(name)
                
                # Execute update
                query = f"UPDATE users SET {', '.join(update_fields)} WHERE name = ?"
                cursor.execute(query, update_values)
                conn.commit()
                
                print(f"User '{name}' updated successfully")
                return True
                
        except Exception as e:
            print(f"Error updating user: {e}")
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
                    SELECT id, name, password_hash, age, city, income, expenses,
                           totalDebt, totalAmountInAccount, employment, netIncome, context,
                           housing_situation, dining_habits, monthly_subscriptions, credit_score,
                           financial_goal, financial_confidence_score
                    FROM users WHERE name = ?
                ''', (name,))
                row = cursor.fetchone()
                
                if not row:
                    print(f"User '{name}' not found")
                    return None
                
                # Decrypt and return user data
                user = {
                    'id': row[0],
                    'name': row[1],
                    'password_hash': row[2],
                    'age': self._decrypt_field(row[3]),
                    'location': self._decrypt_field(row[4]), # Map 'city' from DB to 'location' for frontend
                    'monthly_income': self._decrypt_field(row[5]),
                    'monthly_expenses': self._decrypt_field(row[6]),
                    'total_debt': self._decrypt_field(row[7]),
                    'bank_account_balance': self._decrypt_field(row[8]),
                    'employment_status': self._decrypt_field(row[9]),
                    'netIncome': self._decrypt_field(row[10]),
                    'past_conversation_context': self._decrypt_field(row[11]),
                    'housing_situation': self._decrypt_field(row[12]),
                    'dining_habits': self._decrypt_field(row[13]),
                    'monthly_subscriptions': self._decrypt_field(row[14]),
                    'credit_score': self._decrypt_field(row[15]),
                    'financial_goal': self._decrypt_field(row[16]),
                    'financial_confidence_score': self._decrypt_field(row[17])
                }
                
                print(f"User '{name}' retrieved and decrypted")
                return user
                
        except Exception as e:
            print(f"Error retrieving user: {e}")
            return None
        
    def get_user_field(self, name, field='context'):
        """
        Retrieve and decrypt a specific field of user data by name
        
        Args:
            name: Name of the user
            field: Field to retrieve
            
        Returns:
            Decrypted field value, or None if not found
        """
        try:
            with self as conn:
                cursor = conn.cursor()
                cursor.execute(f'''
                    SELECT {field} FROM users WHERE name = ?
                ''', (name,))
                row = cursor.fetchone()
                
                if not row:
                    print(f"User '{name}' not found")
                    return None
                
                decrypted_value = self._decrypt_field(row[0])
                print(f"Field '{field}' for user '{name}' retrieved and decrypted")
                return decrypted_value
                
        except Exception as e:
            print(f"Error retrieving field '{field}' for user '{name}': {e}")
            return None


# Interactive Menu
if __name__ == "__main__":
    import sys
    # Check if correct number of arguments provided
    if len(sys.argv) != 3:
        print("Usage: python dbManager.py <json_file> <action_number>")
        print("\nActions:")
        print("  1 - Add new user")
        print("  2 - Pull user data")
        print("  3 - Update user")
        print("  4 - Pull field from specific user")
        sys.exit(1)
    
    json_file = sys.argv[1]
    action = sys.argv[2]
    
    # Validate JSON file exists
    if not os.path.exists(json_file):
        print(f"Error: File '{json_file}' not found")
        sys.exit(1)
    
    # Validate action number
    if action not in ['1', '2', '3', '4']:
        print(f"Error: Invalid action '{action}'. Must be 1, 2, 3, or 4")
        sys.exit(1)
    
    # Get password from environment variable
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'my_super_secret_password')
    
    # Initialize database
    db = UserDatabase(db_name='user.db', password=DB_PASSWORD)
    db.create_table()
    
    # Load JSON data
    try:
        with open(json_file, 'r') as f:
            user_data = json.load(f)
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in '{json_file}'")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)
    
    # Execute action
    if action == '1':
        # Add new user
        success = db.save_user(user_data)
        if success:
            print(f"SUCCESS: User added from {json_file}")
            sys.exit(0)
        else:
            print(f"FAILED: Could not add user")
            sys.exit(1)
    
    elif action == '2':
        # Pull user data
        name = user_data.get('name')
        if not name:
            print("Error: JSON must contain 'name' field for pulling data")
            sys.exit(1)
        
        retrieved_data = db.get_user(name)
        if retrieved_data:
            # Output as JSON to stdout
            print(json.dumps(retrieved_data, indent=2))
            sys.exit(0)
        else:
            print(f"FAILED: User '{name}' not found")
            sys.exit(1)
    
    elif action == '3':
        # Update user
        name = user_data.get('name')
        if not name:
            print("Error: JSON must contain 'name' field for updating")
            sys.exit(1)
        
        # Remove 'name' from update data as it's used for identification
        update_data = {k: v for k, v in user_data.items() if k != 'name'}
        
        if not update_data:
            print("Error: No fields to update (only 'name' was provided)")
            sys.exit(1)
        
        success = db.update_user(name, update_data)
        if success:
            print(f"SUCCESS: User '{name}' updated")
            sys.exit(0)
        else:
            print(f"FAILED: Could not update user '{name}'")
            sys.exit(1)
    
    elif action == '4':
        # Pull field from specific user
        name = user_data.get('name')

        retrieved_field = db.get_user_field(name)
        if retrieved_field is not None:
            print(retrieved_field)
            sys.exit(0)
        else:
            print(f"FAILED: Could not retrieve context for user '{name}'")
            sys.exit(1)
