from web3 import Web3
import os

# ----- Handle both web3 v6 and v5 for POA middleware -----
try:
    # web3 v6+
    from web3.middleware.proof_of_authority import ExtraDataToPOAMiddleware
    Middleware = ExtraDataToPOAMiddleware
except ImportError:
    # web3 v5
    from web3.middleware import geth_poa_middleware
    Middleware = geth_poa_middleware

# ---------- CONFIG ----------
RPC_URL  = "https://api.avax-test.network/ext/bc/C/rpc"  # Avalanche Fuji
CHAIN_ID = 43113
CONTRACT = Web3.to_checksum_address("0x85ac2e065d4526FBeE6a2253389669a12318A412")
PRIVATE_KEY = "0xf6a2bf61cb37b41d6378e7ce4575ca094f0261035b5ceadaaad10431ad721d41"

w3 = Web3(Web3.HTTPProvider(RPC_URL))
w3.middleware_onion.inject(Middleware, layer=0)

acct = w3.eth.account.from_key(PRIVATE_KEY)
ADDR = acct.address
print("Using address:", ADDR)

# ---------- HELPERS ----------
def fn_selector(sig: str) -> bytes:
    """First 4 bytes of keccak(signature) as BYTES (no 0x)."""
    return Web3.keccak(text=sig)[:4]

def pad32_uint(x: int) -> bytes:
    return x.to_bytes(32, "big")

def pad32_addr(addr: str) -> bytes:
    return bytes.fromhex(addr[2:]).rjust(32, b"\x00")

# ---------- 1) claim(bytes32 nonce) ----------
print("\n=== claim(bytes32) ===")
selector = fn_selector("claim(bytes32)")        # 4 bytes
nonce_bytes = os.urandom(32)                    # 32 bytes
calldata = selector + nonce_bytes               # BYTES concat
data_hex = Web3.to_hex(calldata)                # single 0x-prefixed string
print("nonce:", Web3.to_hex(nonce_bytes))

tx = {
    "to": CONTRACT,
    "from": ADDR,
    "nonce": w3.eth.get_transaction_count(ADDR),
    "data": data_hex,
    "chainId": CHAIN_ID,
    "gas": 100000,
    "maxFeePerGas": w3.to_wei("40", "gwei"),
    "maxPriorityFeePerGas": w3.to_wei("1", "gwei"),
}

signed = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
print("claim tx:", tx_hash.hex())
rcpt = w3.eth.wait_for_transaction_receipt(tx_hash)
print("claim status (1=success):", rcpt.status)

# ---------- 2) balanceOf(address) ----------
print("\n=== balanceOf(address) ===")
sel_bal = fn_selector("balanceOf(address)")
calldata_bal = sel_bal + pad32_addr(ADDR)
bal_hex = w3.eth.call({"to": CONTRACT, "data": Web3.to_hex(calldata_bal)}).hex()
balance = int(bal_hex, 16)
print(f"balanceOf({ADDR}) =", balance)
