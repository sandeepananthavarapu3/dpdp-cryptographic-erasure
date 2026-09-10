import os
import json
import uuid
import base64
import requests
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from web3 import Web3

# --- IMPORT YOUR CUSTOM TSS ENGINE ---
from crypto_engine import SecureErasureEngine

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- BLOCKCHAIN CONFIGURATION ---
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))

contract_address = w3.to_checksum_address("0x5fbdb2315678afecb367f032d93f642f64180aa3")
admin_address = w3.to_checksum_address("0xf39fd6e51aad88f6f4ce6ab8827279cfffb92266")
private_key = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"

contract_abi = json.loads('''
[
    {"inputs": [], "stateMutability": "nonpayable", "type": "constructor"},
    {"inputs": [{"internalType": "string", "name": "_fileId", "type": "string"}], "name": "checkStatus", "outputs": [{"internalType": "bool", "name": "exists", "type": "bool"}, {"internalType": "bool", "name": "deleted", "type": "bool"}], "stateMutability": "view", "type": "function"},
    {"inputs": [{"internalType": "string", "name": "_fileId", "type": "string"}], "name": "registerFile", "outputs": [], "stateMutability": "nonpayable", "type": "function"},
    {"inputs": [{"internalType": "string", "name": "_fileId", "type": "string"}], "name": "triggerDeletion", "outputs": [], "stateMutability": "nonpayable", "type": "function"}
]
''')

contract = w3.eth.contract(address=contract_address, abi=contract_abi)

# --- IPFS (PINATA) CONFIGURATION ---
PINATA_JWT = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySW5mb3JtYXRpb24iOnsiaWQiOiIzNmFhNjdhMC1iNGFiLTQ4NjYtYjlkYy02YmIyYWYwMDZhNjAiLCJlbWFpbCI6Im1jbDIwMjUwMTRAaWlpdGEuYWMuaW4iLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwicGluX3BvbGljeSI6eyJyZWdpb25zIjpbeyJkZXNpcmVkUmVwbGljYXRpb25Db3VudCI6MSwiaWQiOiJGUkExIn0seyJkZXNpcmVkUmVwbGljYXRpb25Db3VudCI6MSwiaWQiOiJOWUMxIn1dLCJ2ZXJzaW9uIjoxfSwibWZhX2VuYWJsZWQiOmZhbHNlLCJzdGF0dXMiOiJBQ1RJVkUifSwiYXV0aGVudGljYXRpb25UeXBlIjoic2NvcGVkS2V5Iiwic2NvcGVkS2V5S2V5IjoiOGEyNjI0NDRmMzMxZmU3NGNjMDQiLCJzY29wZWRLZXlTZWNyZXQiOiJhMGE4ZTdkNzY5M2M2YzY5OTAyODgzMWZkNmVjNGFmYzE3NjNlZjEzNmU5MDQ1MDQyN2I3ZTFkMmUzZDUxNTdiIiwiZXhwIjoxODA3ODEwNzQwfQ.rJtxe4-wPpQIURYzb3Vl2HOJhVnzpgdhC5vB4YL9hp8"  # <--- PASTE YOUR KEY HERE
PINATA_HEADERS = {
    "Authorization": f"Bearer {PINATA_JWT}"
}

# --- PRIVACY ENGINE INITIALIZATION ---
# 3-of-5 Threshold Signature Setup
tss_engine = SecureErasureEngine(threshold=3, total_shares=5)

# Simulated Distributed Vault (In-Memory Database for M.Tech Demo)
# Now ONLY holds the IPFS CID and Key Shares! The Data is decentralized.
DATABASE_VAULT = {}

@app.get("/")
async def home():
    return {"status": "DPDP Crypto-Shredding Server Active", "docs": "/docs"}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    file_id = str(uuid.uuid4())
    try:
        # 1. Read actual file data
        file_data = await file.read()
        
        # 2. Cryptographic Splitting (TSS)
        print(f"[{file_id}] Encrypting and splitting key...")
        ciphertext, shares = tss_engine.encrypt_and_split(file_data)
        
        # 3. PUSH ENCRYPTED PAYLOAD TO IPFS
        print(f"[{file_id}] Pushing encrypted payload to IPFS network...")
        files = {'file': (f"{file_id}.enc", ciphertext)}
        ipfs_res = requests.post("https://api.pinata.cloud/pinning/pinFileToIPFS", files=files, headers=PINATA_HEADERS)
        
        if ipfs_res.status_code != 200:
            print(ipfs_res.text)
            raise Exception("Failed to upload to IPFS via Pinata")
            
        ipfs_data = ipfs_res.json()
        ipfs_cid = ipfs_data["IpfsHash"]
        print(f"[{file_id}] Successfully stored on IPFS! CID: {ipfs_cid}")
        
        # 4. Store in Vault (Only the CID and Shares)
        DATABASE_VAULT[file_id] = {
            "ipfs_cid": ipfs_cid,
            "shares": shares,
            "filename": file.filename
        }
        
        # 5. Log to Blockchain
        nonce = w3.eth.get_transaction_count(admin_address)
        txn_dict = contract.functions.registerFile(file_id).build_transaction({
            'from': admin_address,
            'nonce': nonce,
            'gasPrice': w3.eth.gas_price
        })
        txn_dict['gas'] = w3.eth.estimate_gas(txn_dict)
        signed_txn = w3.eth.account.sign_transaction(txn_dict, private_key=private_key)
        tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
        
        return {
            "status": "Success",
            "message": "File encrypted, sent to IPFS, and key split into 5 shares.",
            "file_id": file_id,
            "ipfs_cid": ipfs_cid,
            "blockchain_tx": tx_hash.hex()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/access/{file_id}")
async def check_access(file_id: str):
    try:
        # 1. Check Blockchain status
        status = contract.functions.checkStatus(file_id).call()
        exists, deleted = status[0], status[1]
        
        if not exists:
            raise HTTPException(status_code=404, detail="File ID not found on Blockchain")
        if deleted:
            return {"status": "Denied", "message": "Access Revoked: Proof of Erasure exists on Blockchain."}
            
        # 2. Fetch CID from Vault
        vault_record = DATABASE_VAULT.get(file_id)
        if not vault_record:
            raise HTTPException(status_code=404, detail="Data not found in local Vault")
            
        # 3. PULL ENCRYPTED PAYLOAD FROM IPFS
        ipfs_cid = vault_record["ipfs_cid"]
        print(f"[{file_id}] Retrieving encrypted payload from IPFS CID: {ipfs_cid}")
        ipfs_gateway_url = f"https://gateway.pinata.cloud/ipfs/{ipfs_cid}"
        
        fetch_res = requests.get(ipfs_gateway_url)
        if fetch_res.status_code != 200:
            raise HTTPException(status_code=500, detail="Failed to retrieve data from IPFS network")
            
        retrieved_ciphertext = fetch_res.content
            
        # 4. Reconstruct Key using threshold shares (We need 3)
        collected_shares = vault_record["shares"][:tss_engine.threshold] 
        
        try:
            # The engine rebuilds the key and decrypts the IPFS file
            decrypted_data = tss_engine.reconstruct_and_decrypt(
                retrieved_ciphertext, 
                collected_shares
            )
        except Exception as math_err:
            return {"status": "Cryptographic Erasure Confirmed", "detail": str(math_err)}
            
        return {
            "status": "Granted",
            "message": "Data successfully reconstructed using 3/5 TSS shares.",
            "filename": vault_record["filename"],
            "preview_bytes_hex": decrypted_data[:20].hex(),
            "file_data_b64": base64.b64encode(decrypted_data).decode('utf-8')
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/delete/{file_id}")
async def delete_file(file_id: str):
    try:
        # 1. CRYPTOGRAPHIC SHREDDING
        if file_id in DATABASE_VAULT:
            DATABASE_VAULT[file_id]["shares"] = DATABASE_VAULT[file_id]["shares"][:2]
            print(f"[SHREDDING SUCCESS] Destroyed 3 shares for {file_id}. Remaining shares: 2.")

        # 2. Log Proof of Erasure on Blockchain
        nonce = w3.eth.get_transaction_count(admin_address)
        txn_dict = contract.functions.triggerDeletion(file_id).build_transaction({
            'from': admin_address,
            'nonce': nonce,
            'gasPrice': w3.eth.gas_price
        })
        txn_dict['gas'] = w3.eth.estimate_gas(txn_dict)
        signed_txn = w3.eth.account.sign_transaction(txn_dict, private_key=private_key)
        tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
        
        return {
            "status": "Erasure Proven",
            "file_id": file_id,
            "blockchain_tx": tx_hash.hex(),
            "action": "3 out of 5 key shares mathematically destroyed. Data permanently unreadable."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/delete/share/{file_id}/{node_id}")
async def delete_single_share(file_id: str, node_id: int):
    try:
        if file_id not in DATABASE_VAULT:
            raise HTTPException(status_code=404, detail="File not found")
            
        current_shares = DATABASE_VAULT[file_id]["shares"]
        updated_shares = [s for s in current_shares if s[0] != node_id]
        DATABASE_VAULT[file_id]["shares"] = updated_shares
        remaining = len(updated_shares)
        
        return {
            "status": "Share Destroyed",
            "node_killed": node_id,
            "remaining_shares": remaining,
            "threshold_met": remaining >= tss_engine.threshold
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/debug/vault")
async def view_vault_contents():
    safe_vault = {}
    for fid, data in DATABASE_VAULT.items():
        safe_vault[fid] = {
            "filename": data["filename"],
            "ipfs_cid": data["ipfs_cid"], # <--- Now showing the IPFS CID instead of preview!
            "total_shares_remaining": len(data["shares"]),
            "share_coordinates": [f"Node {s[0]}: {str(s[1])[:10]}..." for s in data["shares"]]
        }
    return safe_vault

@app.get("/cloud/storage")
async def view_cloud_storage():
    cloud_view = {}
    for fid, data in DATABASE_VAULT.items():
        cloud_view[fid] = {
            "filename": data["filename"],
            "ipfs_cid": data["ipfs_cid"], # <--- Updated for UI
            "active_nodes": [{"node_id": s[0], "share_data": str(s[1])} for s in data["shares"]]
        }
    return cloud_view

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
