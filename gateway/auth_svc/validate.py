import requests
from flask import Request
from .utils import AUTH_SERVICE_ADDRESS

def auth_header(req: Request):
    try:
        auth_header = req.headers["Authorization"]
    except:
        # Authorization header not present in request
        return None, ("missing credentials", 401)
    
    if not auth_header:
        return None, ("missing credentials", 401)
    
    response = requests.post(
        f"http://{AUTH_SERVICE_ADDRESS}/validate", headers={"Authorization": auth_header})
    
    if response.status_code != 200:
        return None, (response.text, response.status_code)

    return response.text, None
