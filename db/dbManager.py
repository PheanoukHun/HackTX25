import sqlite3
import os
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Random import get_random_bytes
import json

class EncryptedDB:
    def __init__(self, db_name='data.db', password='your_password_here'):
        # database name
        self.db_name = db_name
        # encrypted database name
        self.encrypted_name = db_name + '.enc'
        # password
        self.password = password
        # salt for randomizing data
        self.salt_file = db_name + '.salt'
        # connection to database
        self.conn = None
    
    def __enter__(self):
        """Context manager entry"""
        # decrypt file
        self._decrypt_file()
        # connection to database
        self.conn = sqlite3.connect(self.db_name)
        # return connection
        return self.conn
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        # if we're connected, exit database
        if self.conn:
            self.conn.close()
        # encrypt data
        self._encrypt_file()
    
    def _get_key(self):
        if os.path.exists(self.salt_file):
            with open(self.salt_file, 'rb') as f:
                salt = f.read()
        else:
            salt = get_random_bytes(32)
            with open(self.salt_file, 'wb') as f:
                f.write(salt)
        return PBKDF2(self.password, salt, dkLen=32)
    
    # encrypts an entry
    def _encrypt_file(self):
        # Check if database exists, if not return
        if not os.path.exists(self.db_name):
            return
        
        # Get the encryption key
        key = self._get_key()
        
        # Read the entire database file
        with open(self.db_name, 'rb') as f:
            plaintext = f.read()  # Raw database bytes
        
        # Create AES cipher with the key
        cipher = AES.new(key, AES.MODE_GCM)
        
        # Encrypt the data
        ciphertext, tag = cipher.encrypt_and_digest(plaintext)
        # ciphertext = encrypted data (unreadable)
        # tag = authentication tag (proves data wasn't tampered with)
        
        # Package everything needed to decrypt later
        encrypted_data = {
            # Random value for this encryption
            'nonce': cipher.nonce.hex(),
            # Authentication tag      
            'tag': tag.hex(),
            # The encrypted database                 
            'ciphertext': ciphertext.hex()     
        }
        
        # Save encrypted version
        with open(self.encrypted_name, 'w') as f:
            json.dump(encrypted_data, f)
        
        # Delete the plaintext version for security
        os.remove(self.db_name)
        
    def _decrypt_file(self):
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

# Usage with context manager (cleaner!)
if __name__ == "__main__":
    db = EncryptedDB(password='my_super_secret_password')
    
    # Automatically decrypts on entry, encrypts on exit
    with db as conn:
        c = conn.cursor()
        
        # Create table
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                email TEXT
            )
        ''')
        
        # Insert
        c.execute('INSERT INTO users (username, email) VALUES (?, ?)',
                 ('charlie', 'charlie@example.com'))
        
        # Query
        c.execute('SELECT * FROM users')
        print("Users:", c.fetchall())
        
        conn.commit()
    
    print("✅ Database encrypted and saved!")