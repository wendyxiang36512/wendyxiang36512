from web3 import Web3
from web3.middleware import geth_poa_middleware
import os

# ====== 配置 ======
RPC_URL = "https://api.avax-test.network/ext/bc/C/rpc"   # Avalanche Fuji
CHAIN_ID = 43113
CONTRACT = Web3.to_checksum_address("0x85ac2e065d4526FBeE6a2253389669a12318A412")

PRIVATE_KEY = "0xf6a2bf61cb37b41d6378e7ce4575ca094f0261035b5ceadaaad10431ad721d41"

w3 = Web3(Web3.HTTPProvider(RPC_URL))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)

acct = w3.eth.account.from_key(PRIVATE_KEY)
ADDR = acct.address
print("Using address:", ADDR)

def selector(sig: str) -> bytes:
    return Web3.keccak(text=sig)[:4]

def pad32(x: bytes) -> str:
    return x.rjust(32, b"\x00").hex()


def hexaddr32(addr: str) -> str:
    return pad32(bytes.fromhex(addr[2:]))

sel_claim = selector("claim(bytes32)").hex() 

nonce_bytes = os.urandom(32)
arg_nonce = nonce_bytes.hex()  

data_claim = "0x" + sel_claim + arg_nonce

tx = {
    "to": CONTRACT,
    "from": ADDR,
    "nonce": w3.eth.get_transaction_count(ADDR),
    "data": data_claim,
    "chainId": CHAIN_ID,
    "gas": 300000,
}

base = w3.to_wei("30", "gwei")
tx["maxFeePerGas"] = base
tx["maxPriorityFeePerGas"] = w3.to_wei("1", "gwei")

signed = w3.eth.account.sign_transaction(tx, private_key=PRIVATE_KEY)
tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
print("claim tx sent:", tx_hash.hex())

rcpt = w3.eth.wait_for_transaction_receipt(tx_hash)
print("claim status:", rcpt.status)

sel_balanceOf = selector("balanceOf(address)").hex()
arg_owner = hexaddr32(ADDR)

data_balance = "0x" + sel_balanceOf + arg_owner

call = {
    "to": CONTRACT,
    "data": data_balance,
}

bal_hex = w3.eth.call(call).hex()
balance = int(bal_hex, 16)
print("balanceOf(you) =", balance)
