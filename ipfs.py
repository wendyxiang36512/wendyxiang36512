import requests
import json

# Set your Pinata API credentials here
PINATA_API_KEY = "51257ad2c286b84d9c8e"
PINATA_API_SECRET = "10ea9ae1d83450975db89a8fe8598f98e5b8ca384d5e218cd5705bc1de88678f"

def pin_to_ipfs(data):
    """
    Pins a Python dictionary (as JSON) to IPFS via Pinata and returns the CID.
    
    Parameters:
    - data: A Python dictionary to be stored on IPFS.
    
    Returns:
    - CID (Content Identifier) of the data stored.
    """
    assert isinstance(data, dict), f"Error pin_to_ipfs expects a dictionary"
    
    # Convert the dictionary to JSON
    json_data = json.dumps(data)
    
    # Pinata API URL for pinning data
    url = "https://api.pinata.cloud/pinning/pinFileToIPFS"
    
    # Prepare the file data for upload (upload JSON as a file)
    files = {
        'file': ('data.json', json_data, 'application/json')
    }

    # Pinata authentication headers
    headers = {
        'pinata_api_key': PINATA_API_KEY,
        'pinata_secret_api_key': PINATA_API_SECRET
    }

    # Send the POST request to pin the data to IPFS
    response = requests.post(url, headers=headers, files=files)

    # Check if the request was successful (HTTP status code 200)
    if response.status_code == 200:
        # Extract the CID (Content Identifier) from the response
        cid = response.json()['IpfsHash']
        return cid
    else:
        raise Exception(f"Error pinning data: {response.status_code}, {response.text}")


def get_from_ipfs(cid, content_type="json"):
    """
    Retrieves content from IPFS using the provided CID via Pinata's public gateway.
    
    Parameters:
    - cid: The Content Identifier (CID) of the data stored on IPFS.
    - content_type: The expected content type of the response (default is "json").
    
    Returns:
    - A Python dictionary containing the content from IPFS.
    """
    assert isinstance(cid, str), f"get_from_ipfs accepts a cid in the form of a string"
    
    # Pinata's public IPFS gateway URL for retrieving content by CID
    url = f"https://gateway.pinata.cloud/ipfs/{cid}"

    # Send a GET request to retrieve the content from IPFS
    response = requests.get(url)

    # Check if the request was successful (HTTP status code 200)
    if response.status_code == 200:
        if content_type == "json":
            # Parse the JSON response into a Python dictionary
            data = response.json()
        else:
            # If content type is not JSON, return the raw response text
            data = response.text
    else:
        raise Exception(f"Error retrieving data: {response.status_code}, {response.text}")
    
    # Ensure that the data is a dictionary (only for JSON content)
    assert isinstance(data, dict), f"get_from_ipfs should return a dict"
    
    return data
