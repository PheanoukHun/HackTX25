import sqlite3
import os
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Random import get_random_bytes
import json

class EncryptedDB:
    def __init__(self, db_name='data.db', password='your_password_here'):
        self.db_name = db_name
        self.encrypted_name = db_name + '.enc'
        self.password = password
        self.salt_file = db_name + '.salt'
        self.conn = None
        
    def _get_key(self):
        """Derive encryption key from password"""
        if os.path.exists(self.salt_file):
            with open(self.salt_file, 'rb') as f:
                salt = f.read()
        else:
            salt = get_random_bytes(32)
            with open(self.salt_file, 'wb') as f:
                f.write(salt)
        
        # Derive 256-bit key
        key = PBKDF2(self.password, salt, dkLen=32)
        return key
    
    def _encrypt_file(self):
        """Encrypt the database file"""
        if not os.path.exists(self.db_name):
            return
        
        key = self._get_key()
        
        # Read database file
        with open(self.db_name, 'rb') as f:
            plaintext = f.read()
        
        # Encrypt with AES
        cipher = AES.new(key, AES.MODE_GCM)
        ciphertext, tag = cipher.encrypt_and_digest(plaintext)
        
        # Save encrypted data
        encrypted_data = {
            'nonce': cipher.nonce.hex(),
            'tag': tag.hex(),
            'ciphertext': ciphertext.hex()
        }
        
        with open(self.encrypted_name, 'w') as f:
            json.dump(encrypted_data, f)
        
        # Remove plaintext database
        os.remove(self.db_name)
    
    def _decrypt_file(self):
        """Decrypt the database file"""
        if not os.path.exists(self.encrypted_name):
            return
        
        key = self._get_key()
        
        # Load encrypted data
        with open(self.encrypted_name, 'r') as f:
            encrypted_data = json.load(f)
        
        # Decrypt
        cipher = AES.new(key, AES.MODE_GCM, 
                        nonce=bytes.fromhex(encrypted_data['nonce']))
        plaintext = cipher.decrypt_and_verify(
            bytes.fromhex(encrypted_data['ciphertext']),
            bytes.fromhex(encrypted_data['tag'])
        )
        
        # Save decrypted database
        with open(self.db_name, 'wb') as f:
            f.write(plaintext)
    
    def connect(self):
        """Connect to database (auto-decrypt if needed)"""
        # Decrypt if encrypted version exists
        if os.path.exists(self.encrypted_name):
            self._decrypt_file()
        
        self.conn = sqlite3.connect(self.db_name)
        return self.conn
    
    def close(self):
        """Close connection and re-encrypt"""
        if self.conn:
            self.conn.close()
            self.conn = None
        
        # Re-encrypt the database
        self._encrypt_file()
    
    def execute(self, query, params=None):
        """Execute a query"""
        if not self.conn:
            self.connect()
        
        cursor = self.conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        self.conn.commit()
        return cursor

# Example usage
if __name__ == "__main__":
    # Create encrypted database
    db = EncryptedDB(password='my_super_secret_password')
    
    # Connect (auto-decrypts)
    db.connect()
    
    # Create table
    db.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Insert data
    db.execute('INSERT OR IGNORE INTO users (username, email) VALUES (?, ?)',
              ('alice', 'alice@example.com'))
    db.execute('INSERT OR IGNORE INTO users (username, email) VALUES (?, ?)',
              ('bob', 'bob@example.com'))
    
    # Query data
    cursor = db.execute('SELECT * FROM users')
    users = cursor.fetchall()
    
    print("Users in encrypted database:")
    for user in users:
        print(f"  ID: {user[0]}, Username: {user[1]}, Email: {user[2]}")
    
    # Close (auto-encrypts)
    db.close()
    
    print("\n✅ Database is now encrypted on disk!")
    print(f"   Encrypted file: {db.encrypted_name}")
    print(f"   Salt file: {db.salt_file}")