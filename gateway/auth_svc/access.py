import requests
from flask import Request
from .utils import AUTH_SERVICE_ADDRESS

def login(req: Request):
    auth = req.data
    if not auth:
        return None, ("missing credentials", 401)

    response = requests.post(
        f"http://{AUTH_SERVICE_ADDRESS}/login",
        headers={"Content-Type": "application/json"},
        data=auth
    )
    
    if response.status_code != 200:
        return None, (response.text, response.status_code)
    
    return response.text, None

def signup(req: Request):
    auth = req.data
    if not auth:
        return None, ("missing credentials", 401)

    response = requests.post(
        f"http://{AUTH_SERVICE_ADDRESS}/signup",
        headers={"Content-Type": "application/json"},
        data=auth
    )
    
    if response.status_code != 200:
        return None, (response.text, response.status_code)
    
    return response.text, None
