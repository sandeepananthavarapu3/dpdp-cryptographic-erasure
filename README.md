# DPDP-Compliant Cryptographic Erasure using Threshold Secret Sharing and Smart-Contract Audit Log

This project implements a cryptographic erasure system enforcing India's Digital Personal Data Protection (DPDP) Act Right to Erasure on immutable storage using threshold secret sharing and smart contract audit logging.

## Overview

The system addresses the challenge of permanently deleting data from immutable storage (like IPFS) by implementing cryptographic erasure through Shamir's Secret Sharing, while maintaining compliance with the DPDP Act through blockchain-based audit logging.

## Features

- **Threshold Secret Sharing**: Implements Shamir's secret sharing algorithm to split encryption keys into shares
- **Smart Contract Audit Logging**: Ethereum blockchain integration for immutable audit trails
- **DPDP Act Compliance**: Maps India's DPDP Act requirements to system design
- **Multi-Role Access**: Separate interfaces for principals, fiduciaries, and cloud providers
- **Secure Key Management**: Cryptographic key generation and secure distribution
- **IPFS Integration**: Decentralized storage with cryptographic access control

## Architecture

The system consists of three main components:

1. **Smart Contracts** (Solidity/Hardhat)
   - `DPDPErasure.sol`: Main contract for managing data erasure requests and audit logs
   - Immutable audit trail for compliance verification

2. **Backend** (Python/FastAPI)
   - `main.py`: FastAPI server handling API requests
   - `crypto_engine.py`: Cryptographic operations and secret sharing
   - `tss_demo.py`: Threshold secret sharing demonstration

3. **Frontend** (HTML/JavaScript)
   - `index.html`: Main landing page
   - `principal.html`: Interface for data principals (users)
   - `fiduciary.html`: Interface for data fiduciaries (organizations)
   - `cloud.html`: Interface for cloud storage providers

## Technology Stack

- **Blockchain**: Ethereum, Hardhat, web3.py
- **Smart Contracts**: Solidity
- **Backend**: Python, FastAPI
- **Cryptography**: Shamir's Secret Sharing, AES encryption
- **Storage**: IPFS/Pinata
- **Frontend**: HTML, CSS, JavaScript
- **Database**: SQLite (for local metadata)

## Installation

### Prerequisites

- Node.js and npm
- Python 3.8+
- Git

### Setup

1. Clone the repository:
```bash
git clone https://github.com/sandeepananthavarapu3/dpdp-cryptographic-erasure.git
cd dpdp-cryptographic-erasure
```

2. Install Node.js dependencies:
```bash
npm install
```

3. Set up Python virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

4. Configure environment variables (if needed):
- Create a `.env` file for API keys and sensitive configurations

## Usage

### Deploy Smart Contracts

```bash
npx hardhat compile
npx hardhat node
npx hardhat ignition deploy ./ignition/modules/DPDPErasure.js
```

### Run Backend Server

```bash
python main.py
```

### Access Web Interface

Open `index.html` in your browser to access the main interface.

## DPDP Act Compliance

This system implements the following DPDP Act requirements:

- **Right to Erasure**: Users can request permanent deletion of their data
- **Audit Trail**: All erasure requests are logged on the blockchain
- **Consent Management**: Explicit consent tracking for data processing
- **Data Fiduciary Responsibilities**: Clear role separation and accountability

## Security Features

- Threshold cryptography prevents single point of failure
- Blockchain audit logs ensure transparency and immutability
- Role-based access control
- Secure key generation and distribution
- Encrypted data storage on IPFS

## License

MIT License

## Author

Ananthavarapu Sandeep Chandra
M.Tech in IT (Cyber Laws and Information Security)
Indian Institute of Information Technology, Allahabad
