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
                print(f"User '{name}' saved and encrypted successfully")
                return True
                
        except Exception as e:
            print(f"Error saving user: {e}")
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
                    print(f"User '{name}' not found")
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
                
                print(f"User '{name}' retrieved and decrypted")
                return user
                
        except Exception as e:
            print(f"Error retrieving user: {e}")
            return None


# Example usage
if __name__ == "__main__":
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
                print(f"User '{name}' saved and encrypted successfully")
                return True
                
        except Exception as e:
            print(f"Error saving user: {e}")
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
                    print(f"User '{name}' not found")
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
                
                print(f"User '{name}' retrieved and decrypted")
                return user
                
        except Exception as e:
            print(f"Error retrieving user: {e}")
            return None
        
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
                    'city': 'city',
                    'income': 'income',
                    'expenses': 'expenses',
                    'shouldPayDebt': 'shouldPayDebt',
                    'totalDebt': 'totalDebt',
                    'totalAmountInAccount': 'totalAmountInAccount',
                    'employment': 'employment',
                    'netIncome': 'netIncome'
                }
                
                for field, column in field_map.items():
                    if field in updated_data:
                        update_fields.append(f"{column} = ?")
                        update_values.append(self._encrypt_field(updated_data[field]))
                
                if not update_fields:
                    print("⚠️  No valid fields to update")
                    return False
                
                # Add name to the end for WHERE clause
                update_values.append(name)
                
                # Execute update
                query = f"UPDATE users SET {', '.join(update_fields)} WHERE name = ?"
                cursor.execute(query, update_values)
                conn.commit()
                
                print(f"✅ User '{name}' updated successfully")
                return True
                
        except Exception as e:
            print(f"Error updating user: {e}")
            return False



# Example usage
if __name__ == "__main__":
    import sys
    
    # Default password - you should change this or use environment variable
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'my_super_secret_password')
    
    # Initialize database with password
    db = UserDatabase(db_name='user.db', password=DB_PASSWORD)
    
    # Create table
    db.create_table()
    
    print("=" * 60)
    print("ENCRYPTED USER DATABASE MANAGER")
    print("=" * 60)
    print("\nWhat would you like to do?")
    print("1. Add new user")
    print("2. Pull user data")
    print("3. Update user information")
    print("4. Exit")
    print()
    
    choice = input("Enter your choice (1-4): ").strip()
    
    if choice == '1':
        # Add new user
        print("\n" + "=" * 60)
        print("ADD NEW USER")
        print("=" * 60)
        
        json_file = input("Enter the path to the JSON file: ").strip()
        
        if not os.path.exists(json_file):
            print(f"❌ Error: File '{json_file}' not found")
            sys.exit(1)
        
        try:
            with open(json_file, 'r') as f:
                user_data = json.load(f)
            
            success = db.save_user(user_data)
            
            if success:
                delete = input(f"\n🗑️  Delete the JSON file '{json_file}'? (y/n): ").strip().lower()
                if delete == 'y':
                    os.remove(json_file)
                    print(f"✅ Deleted {json_file}")
        
        except json.JSONDecodeError:
            print(f"❌ Error: Invalid JSON format in '{json_file}'")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    elif choice == '2':
        # Pull user data
        print("\n" + "=" * 60)
        print("PULL USER DATA")
        print("=" * 60)
        
        name = input("Enter the user's name: ").strip()
        
        user_data = db.get_user(name)
        
        if user_data:
            print("\n📊 User Data:")
            print(json.dumps(user_data, indent=2))
            
            save = input(f"\n💾 Save to JSON file? (y/n): ").strip().lower()
            if save == 'y':
                output_file = input(f"Enter filename (default: {name.replace(' ', '_')}_data.json): ").strip()
                if not output_file:
                    output_file = f"{name.replace(' ', '_')}_data.json"
                
                with open(output_file, 'w') as f:
                    json.dump(user_data, f, indent=2)
                print(f"✅ Saved to {output_file}")
    
    elif choice == '3':
        # Update user information
        print("\n" + "=" * 60)
        print("UPDATE USER INFORMATION")
        print("=" * 60)
        
        name = input("Enter the user's name: ").strip()
        
        # Check if user exists first
        existing_user = db.get_user(name)
        if not existing_user:
            print(f"❌ User '{name}' not found")
            sys.exit(1)
        
        print(f"\n📋 Current data for {name}:")
        print(json.dumps(existing_user, indent=2))
        
        print("\n" + "-" * 60)
        print("Update options:")
        print("1. Update from JSON file")
        print("2. Update specific fields manually")
        
        update_choice = input("\nEnter your choice (1-2): ").strip()
        
        if update_choice == '1':
            # Update from JSON file
            json_file = input("Enter the path to the JSON file with updates: ").strip()
            
            if not os.path.exists(json_file):
                print(f"❌ Error: File '{json_file}' not found")
                sys.exit(1)
            
            try:
                with open(json_file, 'r') as f:
                    update_data = json.load(f)
                
                success = db.update_user(name, update_data)
                
                if success:
                    delete = input(f"\n🗑️  Delete the JSON file '{json_file}'? (y/n): ").strip().lower()
                    if delete == 'y':
                        os.remove(json_file)
                        print(f"✅ Deleted {json_file}")
            
            except json.JSONDecodeError:
                print(f"❌ Error: Invalid JSON format in '{json_file}'")
            except Exception as e:
                print(f"❌ Error: {e}")
        
        elif update_choice == '2':
            # Update specific fields manually
            print("\nFields you can update:")
            fields = ['age', 'city', 'income', 'expenses', 'shouldPayDebt', 
                     'totalDebt', 'totalAmountInAccount', 'employment', 'netIncome']
            
            for i, field in enumerate(fields, 1):
                print(f"{i}. {field}")
            
            field_nums = input("\nEnter field numbers to update (comma-separated, e.g., 1,3,5): ").strip()
            
            try:
                indices = [int(x.strip()) - 1 for x in field_nums.split(',')]
                update_data = {}
                
                for idx in indices:
                    if 0 <= idx < len(fields):
                        field = fields[idx]
                        value = input(f"Enter new value for {field}: ").strip()
                        update_data[field] = value
                
                if update_data:
                    db.update_user(name, update_data)
                else:
                    print("⚠️  No fields selected for update")
            
            except ValueError:
                print("❌ Error: Invalid input format")
        
        else:
            print("❌ Invalid choice")
    
    elif choice == '4':
        print("\n👋 Goodbye!")
        sys.exit(0)
    
    else:
        print("❌ Invalid choice. Please select 1-4.")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("OPERATION COMPLETE")
    print("=" * 60)