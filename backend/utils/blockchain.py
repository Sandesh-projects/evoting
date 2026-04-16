from web3 import Web3
import json
import os

# Connect to Ganache
GANACHE_URL = "http://127.0.0.1:7545"
w3 = Web3(Web3.HTTPProvider(GANACHE_URL))

if not w3.is_connected():
    print("❌ ERROR: Could not connect to Ganache. Is it running?")

# Load ABI
try:
    with open("../blockchain/build/contracts/Voting.json", encoding='utf-8') as f:
        contract_json = json.load(f)
    abi = contract_json["abi"]
except FileNotFoundError:
    print("❌ ERROR: Voting.json not found. Did you compile the smart contract?")
    abi = []

# Replace with your newly deployed contract address after migration!
CONTRACT_ADDRESS = "0x1B71325759c0e9058ab1ebc47Ac3C944C2551256"

if abi:
    contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=abi)
    ADMIN_ACCOUNT = w3.eth.accounts[0] # Default Ganache account 0
else:
    contract = None
    ADMIN_ACCOUNT = None