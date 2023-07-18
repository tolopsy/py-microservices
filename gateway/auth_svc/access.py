import requests
from flask import Request
from .utils import AUTH_SERVICE_ADDRESS

def login(req: Request):
    auth = req.authorization
    if not auth:
        return None, ("missing credentials", 401)

    basicAuth = (auth.username, auth.password)

    response = requests.post(
        f"http://{AUTH_SERVICE_ADDRESS}/login",
        auth=basicAuth
    )
    
    if response.status_code != 200:
        return None, (response.text, response.status_code)
    
    return response.text, None
