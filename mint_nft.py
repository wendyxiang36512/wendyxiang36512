import os, json, secrets
from dotenv import load_dotenv
from web3 import Web3
from eth_account import Account


# --- env & RPC ---
load_dotenv()
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
PUBLIC_ADDR = os.getenv("PUBLIC_ADDR")
assert PRIVATE_KEY and PUBLIC_ADDR, "Set PRIVATE_KEY and PUBLIC_ADDR in .env!"

w3 = Web3(Web3.HTTPProvider("https://api.avax-test.network/ext/bc/C/rpc"))

from web3.middleware import ExtraDataToPOAMiddleware
w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)

assert w3.is_connected(), "Failed to connect to Fuji"

# --- load contract ---
with open("abi.json","r") as f:
    ABI = json.load(f)

CONTRACT_ADDR = Web3.to_checksum_address("0x85ac2e065d4526FBeE6a2253389669a12318A412")
contract = w3.eth.contract(address=CONTRACT_ADDR, abi=ABI)

# --- account helpers ---
account = Account.from_key(PRIVATE_KEY)

def exists(token_id: int) -> bool:
 
    try:
        return contract.functions.exists(token_id).call()
    except Exception:
   
        try:
            contract.functions.ownerOf(token_id).call()
            return True
        except Exception:
            return False

def send_txn(func):
    nonce = w3.eth.get_transaction_count(account.address)
    tx = func.build_transaction({
        "from": account.address,
        "nonce": nonce,
        "gas": 400_000,
        "maxFeePerGas": w3.to_wei("40", "gwei"),
        "maxPriorityFeePerGas": w3.to_wei("2", "gwei"),
        "chainId": 43113
    })
    signed = w3.eth.account.sign_transaction(tx, private_key=PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    print("tx:", tx_hash.hex())
    rcpt = w3.eth.wait_for_transaction_receipt(tx_hash)
    if rcpt.status != 1:
        raise RuntimeError("Transaction failed")
    return rcpt

def main():
    print("Using:", account.address)
    print("Balance (wei):", w3.eth.get_balance(account.address))

    if not exists(1):
        print("Attempt combine -> expect tokenId=1")
        try:
    
            send_txn(contract.functions.combine(PUBLIC_ADDR, 14, 15))
            print("combine(14,15) succeeded (likely got 1)")
        except Exception as e:
            print("combine(14,15) reverted:", e)


    if exists(1):
        for k in range(2, 64):
            if not exists(k):
                print(f"Attempt combine -> expect tokenId={k}")
                try:
       
                    send_txn(contract.functions.combine(PUBLIC_ADDR, k, k*(k+1)))
                    print(f"combine for k={k} succeeded")
                    break
                except Exception as e:
                    print(f"combine for k={k} reverted:", e)
        else:

            print("Fallback: claim(random)")
            nonce_bytes = secrets.token_bytes(32)
            send_txn(contract.functions.claim(PUBLIC_ADDR, nonce_bytes))


    bal = contract.functions.balanceOf(PUBLIC_ADDR).call()
    print("balanceOf:", bal)




if __name__ == "__main__":
    main()
