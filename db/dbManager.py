import sqlite3
import os
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Random import get_random_bytes
import json
import base64
import sys


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
                    password TEXT NOT NULL,
                    age INTEGER,
                    location TEXT,
                    totalAmountInAccount INTEGER,
                    employment_status TEXT,
                    housing_situation TEXT,
                    dining_habits TEXT,
                    monthly_subscription INTEGER,
                    monthly_income INTEGER,
                    monthly_expenses INTEGER,
                    total_debt INTEGER,
                    credit_score INTEGER,
                    bank_account_balance INTEGER,
                    financial_goal TEXT,
                    financial_confidence_score INTEGER,
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
                
                # Extract fields - name and password are NOT encrypted
                name = user_data.get('name')
                password = user_data.get('password')
                
                # Prepare data - integers stay as integers, text fields get encrypted
                data = {
                    'age': user_data.get('age'),
                    'location': self._encrypt_field(user_data.get('location')),
                    'totalAmountInAccount': user_data.get('totalAmountInAccount'),
                    'employment_status': self._encrypt_field(user_data.get('employment_status')),
                    'housing_situation': self._encrypt_field(user_data.get('housing_situation')),
                    'dining_habits': self._encrypt_field(user_data.get('dining_habits')),
                    'monthly_subscription': user_data.get('monthly_subscription'),
                    'monthly_income': user_data.get('monthly_income'),
                    'monthly_expenses': user_data.get('monthly_expenses'),
                    'total_debt': user_data.get('total_debt'),
                    'credit_score': user_data.get('credit_score'),
                    'bank_account_balance': user_data.get('bank_account_balance'),
                    'financial_goal': self._encrypt_field(user_data.get('financial_goal')),
                    'financial_confidence_score': user_data.get('financial_confidence_score'),
                    'context': self._encrypt_field(user_data.get('context'))
                }
                
                # Insert into database
                cursor.execute('''
                    INSERT INTO users (
                        name, password, age, location, totalAmountInAccount,
                        employment_status, housing_situation, dining_habits,
                        monthly_subscription, monthly_income, monthly_expenses,
                        total_debt, credit_score, bank_account_balance,
                        financial_goal, financial_confidence_score, context
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    name, password, data['age'], data['location'],
                    data['totalAmountInAccount'], data['employment_status'],
                    data['housing_situation'], data['dining_habits'],
                    data['monthly_subscription'], data['monthly_income'],
                    data['monthly_expenses'], data['total_debt'],
                    data['credit_score'], data['bank_account_balance'],
                    data['financial_goal'], data['financial_confidence_score'],
                    data['context']
                ))
                
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
                
                # Define which fields are integers (not encrypted) vs text (encrypted)
                integer_fields = {
                    'age', 'totalAmountInAccount', 'monthly_subscription', 
                    'monthly_income', 'monthly_expenses', 'total_debt', 
                    'credit_score', 'bank_account_balance', 'financial_confidence_score'
                }
                
                text_fields = {
                    'password', 'location', 'employment_status', 'housing_situation',
                    'dining_habits', 'financial_goal', 'context'
                }
                
                for field in updated_data:
                    if field in integer_fields:
                        update_fields.append(f"{field} = ?")
                        update_values.append(updated_data[field])
                    elif field in text_fields:
                        update_fields.append(f"{field} = ?")
                        if field == 'password':
                            # Password is not encrypted
                            update_values.append(updated_data[field])
                        else:
                            # Other text fields are encrypted
                            update_values.append(self._encrypt_field(updated_data[field]))
                
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
                    SELECT 
                        id, name, password, age, location, totalAmountInAccount,
                        employment_status, housing_situation, dining_habits,
                        monthly_subscription, monthly_income, monthly_expenses,
                        total_debt, credit_score, bank_account_balance,
                        financial_goal, financial_confidence_score, context
                    FROM users 
                    WHERE name = ?
                ''', (name,))
                row = cursor.fetchone()
                
                if not row:
                    print(f"User '{name}' not found")
                    return None
                
                # Decrypt and return user data
                user = {
                    'id': row[0],
                    'name': row[1],
                    'password': row[2],
                    'age': row[3],
                    'location': self._decrypt_field(row[4]),
                    'totalAmountInAccount': row[5],
                    'employment_status': self._decrypt_field(row[6]),
                    'housing_situation': self._decrypt_field(row[7]),
                    'dining_habits': self._decrypt_field(row[8]),
                    'monthly_subscription': row[9],
                    'monthly_income': row[10],
                    'monthly_expenses': row[11],
                    'total_debt': row[12],
                    'credit_score': row[13],
                    'bank_account_balance': row[14],
                    'financial_goal': self._decrypt_field(row[15]),
                    'financial_confidence_score': row[16],
                    'context': self._decrypt_field(row[17])
                }
                
                print(f"User '{name}' retrieved and decrypted")
                return user
                
        except Exception as e:
            print(f"Error retrieving user: {e}")
            return None


def main():
    """
    Main function to handle CLI arguments
    
    Usage:
        python dbManager.py <json_file> <action_number>
    
    Actions:
        1 - Add new user
        2 - Pull user data (json_file should contain {"name": "username"})
        3 - Update user (json_file should contain {"name": "username", ...updated_fields})
        4 - Get specific field(s) (json_file should contain {"name": "username", "fields": ["income", "city"]})
    """
    
    # Check if correct number of arguments provided
    if len(sys.argv) != 3:
        print("Usage: python dbManager.py <json_file> <action_number>")
        print("\nActions:")
        print("  1 - Add new user")
        print("  2 - Pull user data")
        print("  3 - Update user")
        print("  4 - Get specific field(s)")
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
        result = {
            "success": success,
            "action": "add_user",
            "message": f"User added from {json_file}" if success else "Could not add user",
            "name": user_data.get('name')
        }
        print(json.dumps(result))
        sys.exit(0 if success else 1)
    
    elif action == '4':
        # Get specific field(s)
        name = user_data.get('name')
        fields = user_data.get('fields', [])
        
        if not name:
            result = {
                "success": False,
                "action": "get_fields",
                "message": "JSON must contain 'name' field",
                "values": {}
            }
            print(json.dumps(result))
            sys.exit(1)
        
        if not fields or not isinstance(fields, list):
            result = {
                "success": False,
                "action": "get_fields",
                "message": "JSON must contain 'fields' array (e.g., ['income', 'city'])",
                "values": {}
            }
            print(json.dumps(result))
            sys.exit(1)
        
        # Get full user data
        user = db.get_user(name)
        
        if not user:
            result = {
                "success": False,
                "action": "get_fields",
                "message": f"User '{name}' not found",
                "values": {}
            }
            print(json.dumps(result))
            sys.exit(1)
        
        # Extract only requested fields
        values = {}
        for field in fields:
            if field in user:
                values[field] = user[field]
            else:
                values[field] = None
        
        result = {
            "success": True,
            "action": "get_fields",
            "message": f"Retrieved {len(values)} field(s) for user '{name}'",
            "values": values
        }
        print(json.dumps(result))
        sys.exit(0)
    
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
            result = {
                "success": False,
                "action": "update_user",
                "message": "JSON must contain 'name' field for updating",
                "name": None
            }
            print(json.dumps(result))
            sys.exit(1)
        
        # Remove 'name' from update data as it's used for identification
        update_data = {k: v for k, v in user_data.items() if k != 'name'}
        
        if not update_data:
            result = {
                "success": False,
                "action": "update_user",
                "message": "No fields to update (only 'name' was provided)",
                "name": name
            }
            print(json.dumps(result))
            sys.exit(1)
        
        success = db.update_user(name, update_data)
        result = {
            "success": success,
            "action": "update_user",
            "message": f"User '{name}' updated" if success else f"Could not update user '{name}'",
            "name": name,
            "updated_fields": list(update_data.keys())
        }
        print(json.dumps(result))
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()