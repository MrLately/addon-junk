import requests

def get_existing_torrent_id(api_token, torrent_hash):
    headers = {"Authorization": f"Bearer {api_token}"}
    response = requests.get("https://api.real-debrid.com/rest/1.0/torrents", headers=headers)
    if response.status_code == 200:
        torrents = response.json()
        for torrent in torrents:
            if torrent['hash'].lower() == torrent_hash.lower():
                return torrent['id']
    else:
        raise Exception(f"Failed to fetch torrents, status code: {response.status_code}")
    return None

# Example usage (Replace YOUR_API_TOKEN and YOUR_TORRENT_HASH with your actual Real Debrid API token and torrent hash)
api_token = "GERG72PHKIYEALQKY63DZMPVVCCEB4CTVE2AQQR6QB67P77JYZPQ"
torrent_hash = "f92858ed03b6cad9534d06edcfeb7fbd5f5f7243"
torrent_id = get_existing_torrent_id(api_token, torrent_hash)
print(torrent_id)

