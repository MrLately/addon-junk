import httpx
import asyncio

# Constants
IMDB_ID = 'tt1136041'  # Example IMDb ID, replace with the one you need
OMDB_API_KEY = 'c93ebe7f'  # Replace with your actual OMDB API key
APIBAY_URL = "https://apibay.org/q.php"

def get_tpb_trackers():
    """Return a string containing commonly used TPB trackers."""
    trackers = [
        "udp://tracker.coppersurfer.tk:6969/announce",
        "udp://9.rarbg.to:2920/announce",
        "udp://tracker.opentrackr.org:1337",
        "udp://tracker.internetwarriors.net:1337/announce",
        "udp://tracker.leechers-paradise.org:6969/announce",
        "udp://tracker.coppersurfer.tk:6969/announce",
        "udp://tracker.pirateparty.gr:6969/announce",
        "udp://tracker.cyberia.is:6969/announce",
        # Add more trackers if needed
    ]
    return '&tr=' + '&tr='.join(trackers)

async def fetch_title_details(imdb_id: str) -> str:
    omdb_url = f"http://www.omdbapi.com/?i={imdb_id}&apikey={OMDB_API_KEY}"
    async with httpx.AsyncClient() as client:
        response = await client.get(omdb_url)
        if response.status_code != 200:
            print("Error fetching title details from OMDB API.")
            return ""
        data = response.json()
        if 'Error' in data:
            print(f"OMDB API Error: {data['Error']}")
            return ""
        
        if data.get("Type") == "episode":
            series_id = data.get("seriesID")
            series_response = await client.get(f"http://www.omdbapi.com/?i={series_id}&apikey={OMDB_API_KEY}")
            if series_response.status_code != 200 or 'Error' in series_response.json():
                print("Error fetching series details from OMDB API.")
                return ""
            series_data = series_response.json()
            series_title = series_data.get("Title", "").replace(" ", "+")
            season = data.get("Season", "").zfill(2)
            episode = data.get("Episode", "").zfill(2)
            search_term = f"{series_title}+S{season}E{episode}"
        else:
            search_term = data.get("Title", "").replace(" ", "+")
        
        return search_term

async def fetch_torrents(search_term: str) -> list:
    params = {"q": search_term}
    async with httpx.AsyncClient() as client:
        response = await client.get(APIBAY_URL, params=params)
        if response.status_code != 200:
            print("Error fetching torrents from Apibay.")
            return []
        return response.json()

async def search_and_display_torrents(imdb_id: str):
    search_term = await fetch_title_details(imdb_id)
    if not search_term:
        print(f"No search term found for IMDb ID {imdb_id}.")
        return

    torrents = await fetch_torrents(search_term)
    if not torrents:
        print(f"No torrents found for '{search_term.replace('+', ' ')}'.")
        return

    # Filter out torrents with 0 seeders
    torrents_with_seeders = [torrent for torrent in torrents if int(torrent.get('seeders', 0)) > 0]

    if not torrents_with_seeders:
        print(f"No torrents with seeders found for '{search_term.replace('+', ' ')}'.")
        return

    print(f"Found {len(torrents_with_seeders)} torrents with seeders for '{search_term.replace('+', ' ')}':")
    for torrent in torrents_with_seeders:
        title = torrent.get('name')
        magnet_link = f"magnet:?xt=urn:btih:{torrent.get('info_hash')}&dn={title.replace(' ', '+')}{get_tpb_trackers()}"
        seeders = torrent.get('seeders', 'N/A')
        #print(f"\nTitle: {title}\nMagnet: {magnet_link}\nSeeders: {seeders}")

async def main():
    await search_and_display_torrents(IMDB_ID)

if __name__ == "__main__":
    asyncio.run(main())

