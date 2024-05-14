from cryptography.fernet import Fernet
import os

ENCRYPTION_KEY_FILE = 'encryption_key.txt'

def get_encryption_key():
    if os.path.exists(ENCRYPTION_KEY_FILE):
        with open(ENCRYPTION_KEY_FILE, 'rb') as f:
            return f.read()
    else:
        key = Fernet.generate_key()
        with open(ENCRYPTION_KEY_FILE, 'wb') as f:
            f.write(key)
        return key

def get_fernet():
    return Fernet(get_encryption_key())