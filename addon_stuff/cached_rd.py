import httpx
import asyncio

real_debrid_api_token = "GERG72PHKIYEALQKY63DZMPVVCCEB4CTVE2AQQR6QB67P77JYZPQ"  # Ensure you have your actual token here
torrent_hash = "8c257c5bac41d493d89468e2afa90290ccf8e963"  # Keep the hash as a constant for easy modification

async def check_rd_cache(torrent_hash):
    api_url = f"https://api.real-debrid.com/rest/1.0/torrents/instantAvailability/{torrent_hash}"
    headers = {"Authorization": f"Bearer {real_debrid_api_token}"}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(api_url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        # Modify the condition to check for non-empty response specifically indicating cached content
        if torrent_hash in data and data[torrent_hash] and any(value for value in data[torrent_hash].values() if value):
            print("The torrent is cached on Real-Debrid.")
            print(data)
        else:
            print("The torrent is not cached on Real-Debrid.")
            print(data)

if __name__ == "__main__":
    asyncio.run(check_rd_cache(torrent_hash))


