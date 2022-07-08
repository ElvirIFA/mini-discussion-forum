"""
Password hashing and verifications
"""
import hashlib, binascii, os

class Hash:
    def __init__(self):
        return None

    @classmethod
    def hash_password(self, password):
        try:
            salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
            pwdhash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'), 
                                        salt, 100000)
            pwdhash = binascii.hexlify(pwdhash)
            return (salt + pwdhash).decode('ascii')
        except Exception as error:
            print(error)
    
    @classmethod
    def verify_password(self, stored_password, provided_password):
        try:
            salt = stored_password[:64]
            stored_password = stored_password[64:]
            pwdhash = hashlib.pbkdf2_hmac('sha512', 
                                        provided_password.encode('utf-8'), 
                                        salt.encode('ascii'), 
                                        100000)
            pwdhash = binascii.hexlify(pwdhash).decode('ascii')
            return pwdhash == stored_password
        except Exception as error:
            print(error)