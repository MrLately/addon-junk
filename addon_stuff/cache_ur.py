import httpx
import asyncio

real_debrid_api_token = "GERG72PHKIYEALQKY63DZMPVVCCEB4CTVE2AQQR6QB67P77JYZPQ"  # Ensure you have your actual token here
torrent_hash = "8c257c5bac41d493d89468e2afa90290ccf8e963"  # Keep the hash as a constant for easy modification

async def get_unrestricted_link(link):
    api_url = "https://api.real-debrid.com/rest/1.0/unrestrict/link"
    headers = {"Authorization": f"Bearer {real_debrid_api_token}"}
    body = {"link": link}

    async with httpx.AsyncClient() as client:
        response = await client.post(api_url, headers=headers, data=body)
        response.raise_for_status()
        data = response.json()
        return data.get("download", None)  # Return the unrestricted download link

async def check_rd_cache(torrent_hash):
    api_url = f"https://api.real-debrid.com/rest/1.0/torrents/instantAvailability/{torrent_hash}"
    headers = {"Authorization": f"Bearer {real_debrid_api_token}"}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(api_url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        if torrent_hash in data and data[torrent_hash] and 'rd' in data[torrent_hash]:
            print("The torrent is cached on Real-Debrid.")
            # Iterate over the 'rd' key's list
            for item in data[torrent_hash]['rd']:
                for file_id, file_info in item.items():
                    filename = file_info['filename']
                    filesize = file_info['filesize']
                    print(f"Filename: {filename}, Filesize: {filesize}")
                    # Here, you'd convert the filename or another unique identifier into a link, if applicable
                    # For demonstration, assuming a link based on filename (you need to replace this logic with actual link retrieval)
                    link = f"http://example.com/{filename}"  # Placeholder link, replace with actual logic to get the link
                    unrestricted_link = await get_unrestricted_link(link)
                    if unrestricted_link:
                        print(f"Unrestricted Link: {unrestricted_link}")
                        return  # Exit after finding the first unrestricted link
        else:
            print("The torrent is not cached on Real-Debrid.")

if __name__ == "__main__":
    asyncio.run(check_rd_cache(torrent_hash))

