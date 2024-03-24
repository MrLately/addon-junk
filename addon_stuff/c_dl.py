import requests

def check_my_downloads(api_token):
    headers = {"Authorization": f"Bearer {api_token}"}
    response = requests.get("https://api.real-debrid.com/rest/1.0/downloads", headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": "Failed to fetch downloads", "status_code": response.status_code}

api_token = "GERG72PHKIYEALQKY63DZMPVVCCEB4CTVE2AQQR6QB67P77JYZPQ"
downloads = check_my_downloads(api_token)
print(downloads)
