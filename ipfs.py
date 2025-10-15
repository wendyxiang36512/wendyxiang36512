import requests
import json

PINATA_API_KEY = "16f350d0db260ea8d711"
PINATA_API_SECRET = "6cd37cda7735469a14c99e087a6c65c9cf6b27048f996fe246f6612ec89ceda7"

def pin_to_ipfs(data):
	assert isinstance(data,dict), f"Error pin_to_ipfs expects a dictionary"
	#YOUR CODE HERE

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


def get_from_ipfs(cid,content_type="json"):
	assert isinstance(cid,str), f"get_from_ipfs accepts a cid in the form of a string"
	#YOUR CODE HERE	
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
