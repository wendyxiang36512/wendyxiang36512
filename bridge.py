from web3 import Web3
from web3.providers.rpc import HTTPProvider
from web3.middleware import ExtraDataToPOAMiddleware #Necessary for POA chains
from datetime import datetime
import json
import pandas as pd


def connect_to(chain):
    if chain == 'source':  # The source contract chain is avax
        api_url = f"https://api.avax-test.network/ext/bc/C/rpc" #AVAX C-chain testnet

    if chain == 'destination':  # The destination contract chain is bsc
        api_url = f"https://data-seed-prebsc-1-s1.binance.org:8545/" #BSC testnet

    if chain in ['source','destination']:
        w3 = Web3(Web3.HTTPProvider(api_url))
        # inject the poa compatibility middleware to the innermost layer
        w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
    return w3


def get_contract_info(chain, contract_info):
    """
        Load the contract_info file into a dictionary
        This function is used by the autograder and will likely be useful to you
    """
    try:
        with open(contract_info, 'r')  as f:
            contracts = json.load(f)
    except Exception as e:
        print( f"Failed to read contract info\nPlease contact your instructor\n{e}" )
        return 0
    return contracts[chain]



def scan_blocks(chain, contract_info="contract_info.json"):
    """
        chain - (string) should be either "source" or "destination"
        Scan the last 5 blocks of the source and destination chains
        Look for 'Deposit' events on the source chain and 'Unwrap' events on the destination chain
        When Deposit events are found on the source chain, call the 'wrap' function the destination chain
        When Unwrap events are found on the destination chain, call the 'withdraw' function on the source chain
    """

    # This is different from Bridge IV where chain was "avax" or "bsc"
    if chain not in ['source','destination']:
        print( f"Invalid chain: {chain}" )
        return 0
    
        #YOUR CODE HERE


    w3_source = connect_to('source')
    w3_destination = connect_to('destination')

    if w3_source is None or w3_destination is None:
        print("Failed to connect to one of the chains")
        return 0


    try:
        with open(contract_info, "r") as f:
            cfg = json.load(f)
    except Exception as e:
        print(f"Error reading {contract_info}: {e}")
        return 0

    src_info = cfg.get("source")
    dst_info = cfg.get("destination")
    if src_info is None or dst_info is None:
        print("contract_info.json missing 'source' or 'destination' sections")
        return 0

    warden = cfg.get("warden")
    if warden is None:
        print("contract_info.json missing 'warden' section")
        return 0

    warden_address = Web3.to_checksum_address(warden["address"])
    warden_privkey = warden["private_key"]

  
    src_contract = w3_source.eth.contract(
        address=Web3.to_checksum_address(src_info["address"]),
        abi=src_info["abi"]
    )
    dst_contract = w3_destination.eth.contract(
        address=Web3.to_checksum_address(dst_info["address"]),
        abi=dst_info["abi"]
    )


    try:
        latest_src_block = w3_source.eth.block_number
        from_block_src = max(0, latest_src_block - 4)

        deposit_filter = src_contract.events.Deposit.create_filter(
            fromBlock=from_block_src,
            toBlock=latest_src_block
        )
        deposit_events = deposit_filter.get_all_entries()
    except Exception as e:
        print(f"Error fetching Deposit events on source: {e}")
        deposit_events = []

    for ev in deposit_events:
        token = ev["args"]["token"]
        recipient = ev["args"]["recipient"]
        amount = ev["args"]["amount"]

        print(f"[SOURCE] Detected Deposit: token={token}, recipient={recipient}, amount={amount}")


        try:
            nonce = w3_destination.eth.get_transaction_count(warden_address)
            tx = dst_contract.functions.wrap(
                token,
                recipient,
                amount
            ).build_transaction({
                "from": warden_address,
                "nonce": nonce,
                "gas": 500000,
                "gasPrice": w3_destination.eth.gas_price,
                "chainId": w3_destination.eth.chain_id,
            })

            signed = w3_destination.eth.account.sign_transaction(tx, private_key=warden_privkey)
            tx_hash = w3_destination.eth.send_raw_transaction(signed.rawTransaction)
            print(f"[DESTINATION] Sent wrap tx: {tx_hash.hex()}")
        except Exception as e:
            print(f"Error sending wrap tx on destination: {e}")

    try:
        latest_dst_block = w3_destination.eth.block_number
        from_block_dst = max(0, latest_dst_block - 4)

        unwrap_filter = dst_contract.events.Unwrap.create_filter(
            fromBlock=from_block_dst,
            toBlock=latest_dst_block
        )
        unwrap_events = unwrap_filter.get_all_entries()
    except Exception as e:
        print(f"Error fetching Unwrap events on destination: {e}")
        unwrap_events = []

    for ev in unwrap_events:
        underlying = ev["args"]["underlying_token"]
        to_addr = ev["args"]["to"]
        amount = ev["args"]["amount"]

        print(f"[DESTINATION] Detected Unwrap: underlying={underlying}, to={to_addr}, amount={amount}")

        try:
            nonce = w3_source.eth.get_transaction_count(warden_address)
            tx = src_contract.functions.withdraw(
                underlying,
                to_addr,
                amount
            ).build_transaction({
                "from": warden_address,
                "nonce": nonce,
                "gas": 500000,
                "gasPrice": w3_source.eth.gas_price,
                "chainId": w3_source.eth.chain_id,
            })

            signed = w3_source.eth.account.sign_transaction(tx, private_key=warden_privkey)
            tx_hash = w3_source.eth.send_raw_transaction(signed.rawTransaction)
            print(f"[SOURCE] Sent withdraw tx: {tx_hash.hex()}")
        except Exception as e:
            print(f"Error sending withdraw tx on source: {e}")
