import uuid, json



# FUNCTIONS

# Function to generate user id
def generateUserID():
    """
    Generate a UUID in the format 7e3fca50-69af-99b6-34f47da3d0e9.
    """
    return str(uuid.uuid4())

# Function to generate org id
def generateOrgID():
    return 'org-' + str(uuid.uuid4()).replace("-","")[:5]

# Function to parse request datas
def parseData(requestBody):
    # Attempt to decode request body if it's bytes
    if isinstance(requestBody, bytes):
        requestBody = requestBody.decode('utf-8')
    
    # Attempt to parse the request body as JSON
    try:
        data = json.loads(requestBody)
    except (json.JSONDecodeError, TypeError):
        # If parsing fails, assume the request body is not JSON and handle accordingly
        if isinstance(requestBody, dict):
            data = requestBody
        elif isinstance(requestBody, str):
            # Attempt to parse as form data (key1=value1&key2=value2)
            data = dict(item.split("=") for item in requestBody.split("&"))
        else:
            # If the request body is of unknown format, return it as-is
            data = requestBody
    
    return data