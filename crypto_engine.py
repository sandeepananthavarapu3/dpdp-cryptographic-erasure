import base64
from cryptography.fernet import Fernet
import shamirs

# We use the 13th Mersenne Prime as our finite field modulus.
# This ensures our 256-bit AES key is strictly smaller than the prime modulus.
LARGE_PRIME = (2**521) - 1

class SecureErasureEngine:
    def __init__(self, threshold=3, total_shares=5):
        self.threshold = threshold
        self.total_shares = total_shares

    def encrypt_and_split(self, plaintext_data: bytes):
        # 1. Generate Master Key (DEK)
        dek = Fernet.generate_key()
        cipher = Fernet(dek)
        
        # 2. Encrypt the actual file data
        ciphertext = cipher.encrypt(plaintext_data)
        
        # 3. Convert Key to Integer for Math Operations
        dek_int = int.from_bytes(base64.urlsafe_b64decode(dek), 'big')
        
        # 4. Split the Key using Shamir's Secret Sharing
        shares = shamirs.shares(
            dek_int, 
            quantity=self.total_shares, 
            threshold=self.threshold,
            modulus=LARGE_PRIME
        )
        return ciphertext, shares

    def reconstruct_and_decrypt(self, ciphertext: bytes, collected_shares: list):
        if len(collected_shares) < self.threshold:
            raise ValueError(f"Insufficient shares. Need {self.threshold}, got {len(collected_shares)}.")
            
        try:
            # FIXED: Added the modulus parameter to the interpolation!
            reconstructed_dek_int = shamirs.interpolate(
                collected_shares, 
                threshold=self.threshold,
                modulus=LARGE_PRIME 
            )
            
            # Convert back to Fernet Key format
            reconstructed_dek_bytes = reconstructed_dek_int.to_bytes(32, 'big')
            reconstructed_dek = base64.urlsafe_b64encode(reconstructed_dek_bytes)
            
            # Decrypt the data
            cipher = Fernet(reconstructed_dek)
            return cipher.decrypt(ciphertext)
        except Exception as e:
            raise ValueError(f"Decryption failed or wrong shares provided: {str(e)}")
