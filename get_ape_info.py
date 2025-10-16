from web3 import Web3
from web3.providers.rpc import HTTPProvider
import requests
import json

bayc_address = "0xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D"
contract_address = Web3.to_checksum_address(bayc_address)

# You will need the ABI to connect to the contract
# The file 'abi.json' has the ABI for the bored ape contract
# In general, you can get contract ABIs from etherscan
# https://api.etherscan.io/api?module=contract&action=getabi&address=0xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D
with open('ape_abi.json', 'r') as f:
    abi = json.load(f)

############################
# Connect to an Ethereum node
api_url = "https://mainnet.infura.io/v3/a18008fa878e4d99bd699920020c7cfd"  # YOU WILL NEED TO PROVIDE THE URL OF AN ETHEREUM NODE
provider = HTTPProvider(api_url)
web3 = Web3(provider)


def get_ape_info(ape_id):
    assert isinstance(ape_id, int), f"{ape_id} is not an int"
    assert 0 <= ape_id, f"{ape_id} must be at least 0"
    assert 9999 >= ape_id, f"{ape_id} must be less than 10,000"

    data = {'owner': "", 'image': "", 'eyes': ""}

    # YOUR CODE HERE

    contract = web3.eth.contract(address=contract_address, abi=abi)

    owner = contract.functions.ownerOf(ape_id).call()
    token_uri = contract.functions.tokenURI(ape_id).call()
    data['owner'] = Web3.to_checksum_address(owner)

    def fetch_ipfs_json(ipfs_uri: str, timeout: int=20) -> dict:
        if not isinstance(ipfs_uri, str) or not ipfs_uri:
            raise ValueError(f"Invalid tokenURI")
        if ipfs_uri.startswith("ipfs://"):
            path = ipfs_uri[len("ipfs://"):]
            if "/" in path:
                cid, subpath = path.split("/", 1)
            else:
                cid, subpath = path, ""
            gateways = [
                f"https://gateway.pinata.cloud/ipfs/{cid}/{subpath}",
                f"https://ipfs.io/ipfs/{cid}/{subpath}",
                f"https://cloudflare-ipfs.com/ipfs/{cid}/{subpath}",
            ]
            headers = {"Accept": "application/json"}
            last_err = None
            for url in gateways:
                try:
                    r = requests.get(url, headers=headers, timeout=timeout)
                    if r.status_code == 200:
                        return r.json()
                except Exception as e:
                    last_err = e
            raise RuntimeError(f"Failed to fetch IPFS JSON for {ipfs_uri}: {last_err}")
        else:
            r = requests.get(ipfs_uri, timeout=timeout)
            r.raise_for_status()
            return r.json()

    metadata = fetch_ipfs_json(token_uri)  

    data['image'] = metadata.get("image") or metadata.get("image_url") or ""

    eyes_val = ""
    attrs = metadata.get("attributes") or metadata.get("traits") or []

    if isinstance(attrs, list):
        for attr in attrs:
            try:
                if str(attr.get("trait_type","")).strip().lower() == "eyes":
                    eyes_val = str(attr.get("value", ""))
                    break
            except Exception:
                pass
    if not eyes_val:
        eyes_val = metadata.get("Eyes") or metadata.get("eyes") or ""
    data['eyes'] = eyes_val                    

    assert isinstance(data, dict), f'get_ape_info{ape_id} should return a dict'
    assert all([a in data.keys() for a in
                ['owner', 'image', 'eyes']]), f"return value should include the keys 'owner','image' and 'eyes'"
    return data
