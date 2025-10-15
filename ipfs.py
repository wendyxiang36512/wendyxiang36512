import requests
import json

def pin_to_ipfs(data):
    assert isinstance(data, dict), f"Error pin_to_ipfs expects a dictionary"
    
    # Convert the dictionary to JSON
    json_data = json.dumps(data)
    
    # Infura IPFS API URL for adding data
    url = "https://ipfs.infura.io:5001/api/v0/add"
    project_id = 'a18008fa878e4d99bd699920020c7cfd'  # Your Infura Project ID
    
    # Headers for authentication with Infura (Bearer token authorization)
    headers = {
        'Authorization': f'Bearer {project_id}',  # Correct Bearer token format
        'Content-Type': 'application/json'
    }
    
    # Prepare the file data for upload (upload JSON as a file)
    files = {
        'file': ('data.json', json_data, 'application/json')  # Simulate uploading a JSON file
    }

    # Send the POST request to pin the data to IPFS
    response = requests.post(url, headers=headers, files=files)

    # Check if the request was successful (HTTP status code 200)
    if response.status_code == 200:
        # Extract the CID (Content Identifier) from the response
        cid = response.json()['Hash']
        return cid
    else:
        raise Exception(f"Error pinning data: {response.status_code}, {response.text}")


def get_from_ipfs(cid, content_type="json"):
    assert isinstance(cid, str), f"get_from_ipfs accepts a cid in the form of a string"
    
    # Infura IPFS gateway URL for retrieving content by CID
    url = f"https://ipfs.infura.io:5001/api/v0/cat?arg={cid}"
    project_id = 'a18008fa878e4d99bd699920020c7cfd'  # Your Infura Project ID

    # Send a GET request to the Infura IPFS gateway to retrieve the content (Bearer token authentication)
    response = requests.get(url, headers={'Authorization': f'Bearer {project_id}'})

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
