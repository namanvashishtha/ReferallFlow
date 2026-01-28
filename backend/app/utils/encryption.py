from cryptography.fernet import Fernet
from app.core.config import settings
import base64


class CredentialEncryption:
    def __init__(self):
        key = settings.ENCRYPTION_KEY.encode()
        if len(key) < 32:
            key = key.ljust(32, b'\0')
        elif len(key) > 32:
            key = key[:32]
        
        key_b64 = base64.urlsafe_b64encode(key)
        self.cipher = Fernet(key_b64)
    
    def encrypt(self, plaintext: str) -> str:
        encrypted = self.cipher.encrypt(plaintext.encode())
        return encrypted.decode()
    
    def decrypt(self, encrypted_text: str) -> str:
        decrypted = self.cipher.decrypt(encrypted_text.encode())
        return decrypted.decode()


credential_encryption = CredentialEncryption()
