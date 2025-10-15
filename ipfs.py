import requests
import json

def pin_to_ipfs(data):
	assert isinstance(data,dict), f"Error pin_to_ipfs expects a dictionary"
	#YOUR CODE HERE

	json_data = json.dumps(data)

	url = "https://ipfs.infura.io:5001/api/v0/add" 
	project_id = "a18008fa878e4d99bd699920020c7cfd"



	headers = {
			'Authorization': f'Bearer{project_id}',
			'Content-Type': 'application/json'
	}

	files = {
	    'file': ('data.json', json_data, 'application/json')	
	}

	response = requests.post(url, headers=headers, files=files)

	if response.status_code == 200:
		cid = response.json()['Hash']
		return cid
	else:
		raise Exception (f"Error pinning data: {response.status_code}, {response.text}")

def get_from_ipfs(cid,content_type="json"):
	assert isinstance(cid,str), f"get_from_ipfs accepts a cid in the form of a string"
	#YOUR CODE HERE	
	url = f"https://ipfs.infura.io:5001/api/v0/cat?arg={cid}"
	project_id = "a18008fa878e4d99bd699920020c7cfd"

	headers = {'Authorization': f'Bearer {project_id}'} 

	response = requests.post(url, headers=headers)

	if response.status_code ==200:
		if content_type == "json":
			data= response.json()
		else:
			data = response.text
	else:		
		raise Exception(f"Error retrieving data: {response.status_code}, {response.text}")
    	


	assert isinstance(data,dict), f"get_from_ipfs should return a dict"
	return data
