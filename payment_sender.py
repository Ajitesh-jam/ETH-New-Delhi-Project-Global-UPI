from web3 import Web3
import json
import os

CHAIN_CONFIG = {
    "ETH": {
        "rpc": "https://sepolia.infura.io/v3/490a392c2a854d1387b486166f7d1dfa",
        "contract": "0x7B2f8442e4e4bf1F84FFb38C2709C742e9bb3150",
        "symbol": "ETH",
        "gas_price_gwei": 10
    },
    "MATIC": {
        "rpc": "https://polygon-amoy.infura.io/v3/490a392c2a854d1387b486166f7d1dfa",
        "contract": "0xEdfeB26543baD79CD58aff55eD4484D515a769e7",
        "symbol": "MATIC",
        "gas_price_gwei": 50
    },
    "RSK": {
        "rpc": "https://public-node.testnet.rsk.co",
        "contract": "0xRSKContractAddress",
        "symbol": "RBTC",
        "gas_price_gwei": 20
    }
}


PRIVATE_KEY = os.getenv("PRIVATE_KEY")
if not PRIVATE_KEY:
    raise ValueError("Set PRIVATE_KEY environment variable")

try:
    with open('PaymentSender.json', 'r') as f:
        CONTRACT_ARTIFACT = json.load(f)
except FileNotFoundError:
    print("Error: 'contract_artifact.json' not found. Please create this file with your contract's build artifact.")
    exit()

ABI = CONTRACT_ARTIFACT['abi']

def send_native(chain: str, recipient: str, amount: float):
    """Send native coin (ETH, POL, etc.) through the smart contract on any supported chain"""
    if not PRIVATE_KEY or "YOUR_PRIVATE_KEY_HERE" in PRIVATE_KEY:
        raise ValueError("Please replace 'YOUR_PRIVATE_KEY_HERE' with your actual private key.")
        
    if chain not in CHAIN_CONFIG:
        raise ValueError(f"Unsupported chain: {chain}")

    config = CHAIN_CONFIG[chain]
    w3 = Web3(Web3.HTTPProvider(config["rpc"]))
    
    if not w3.is_connected():
        raise ConnectionError(f"Failed to connect to {chain} RPC at {config['rpc']}")

    account = w3.eth.account.from_key(PRIVATE_KEY)

    contract = w3.eth.contract(address=config["contract"], abi=ABI)
    

    amount_wei = w3.to_wei(amount, "ether")

    print(f"Building transaction for {amount} ETH ({amount_wei} wei) to {recipient} on {chain}...")

    txn = contract.functions.send(recipient, amount_wei).build_transaction({
        "from": account.address,
        "value": amount_wei,
        "nonce": w3.eth.get_transaction_count(account.address),
        "gas": 200000,
        "gasPrice": w3.to_wei(config["gas_price_gwei"], "gwei")
    })

    signed_txn = w3.eth.account.sign_transaction(txn, PRIVATE_KEY)
    
    tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
    
    
    return w3.to_hex(tx_hash)


