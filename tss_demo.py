import base64
import shamirs
from cryptography.fernet import Fernet

# The finite field modulus (13th Mersenne Prime)
LARGE_PRIME = (2**521) - 1

def run_tss_demo():
    print("\n" + "="*50)
    print("   THRESHOLD SECRET SHARING (TSS) DEMO")
    print("   Simulating a 3-of-5 Distributed Privacy Setup")
    print("="*50 + "\n")

    # --- STEP 1: GENERATE THE SECRET ---
    master_key = Fernet.generate_key()
    secret_int = int.from_bytes(base64.urlsafe_b64decode(master_key), 'big')
    print(f"[PHASE 1] Data Encryption Key (DEK) Generated.")
    print(f"          Original Key: {master_key[:20]}...\n")

    # --- STEP 2: SPLIT THE SECRET ---
    print(f"[PHASE 2] Splitting Key into 5 Shares (Threshold = 3)...")
    shares = shamirs.shares(secret_int, quantity=5, threshold=3, modulus=LARGE_PRIME)
    
    for i, share in enumerate(shares, 1):
        # share[0] is the X coordinate, share[1] is the Y coordinate
        print(f"          -> Node {i} receives Share (X={share[0]}): {str(share[1])[:15]}...")

    # --- STEP 3: SUCCESSFUL RECONSTRUCTION ---
    print("\n[PHASE 3] SCENARIO A: Authorized Access (3/5 Shares)")
    print("          System gathers shares from Node 1, 3, and 5...")
    
    collected_shares = [shares[0], shares[2], shares[4]] 
    reconstructed_int = shamirs.interpolate(collected_shares, threshold=3, modulus=LARGE_PRIME)
    reconstructed_key = base64.urlsafe_b64encode(reconstructed_int.to_bytes(32, 'big'))
    
    if master_key == reconstructed_key:
        print("          [✓] Math matches! Key successfully reconstructed.")
        print("          [✓] Data can be decrypted and accessed.")

    # --- STEP 4: CRYPTOGRAPHIC ERASURE ---
    print("\n[PHASE 4] SCENARIO B: Cryptographic Erasure (DPDP Right to Erasure)")
    print("          User requests deletion. Nodes 3, 4, and 5 destroy their shares.")
    print("          Only 2 shares remain in the system.")
    
    remaining_shares = [shares[0], shares[1]] 
    
    print("          Attempting to reconstruct the Master Key with 2 shares...")
    
    try:
        # Trying to map a polynomial curve with only 2 points will trigger a mathematical error!
        wrong_int = shamirs.interpolate(remaining_shares, threshold=3, modulus=LARGE_PRIME)
    except ValueError as e:
        print(f"          [✓] System rejected reconstruction: {e}")
        print("          [✓] Math fails! The reconstructed key is impossible to generate.")
        print("\n          [SUCCESS] Cryptographic Erasure Achieved.")
        print("          The encrypted data is now permanently mathematically unreadable.")
        
    print("\n" + "="*50 + "\n")

if __name__ == "__main__":
    run_tss_demo()
