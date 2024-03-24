import httpx
import asyncio

# Constants
IMDB_ID = 'tt4236770'  # The Shawshank Redemption
#IMDB_ID = 'tt6674736'  # S12.E24 The Date Night Variable, The Big Bang Theory
OMDB_API_KEY = 'c93ebe7f'  # Replace with your actual OMDB API key
APIBAY_URL = "https://apibay.org/q.php"

async def fetch_title_details(imdb_id: str) -> str:
    """Fetch title details using IMDb ID from OMDB API, handling both movies and series episodes."""
    omdb_url = f"http://www.omdbapi.com/?i={imdb_id}&apikey={OMDB_API_KEY}"
    async with httpx.AsyncClient() as client:
        response = await client.get(omdb_url)
        response.raise_for_status()
        data = response.json()
        
        if data.get("Type") == "episode":
            series_id = data.get("seriesID")
            series_response = await client.get(f"http://www.omdbapi.com/?i={series_id}&apikey={OMDB_API_KEY}")
            series_data = series_response.json()
            series_title = series_data.get("Title", "").replace(" ", "+")
            
            season = data.get("Season", "").zfill(2)
            episode = data.get("Episode", "").zfill(2)
            search_term = f"{series_title}+S{season}E{episode}"
        else:
            search_term = data.get("Title", "").replace(" ", "+")
        
        return search_term

async def fetch_torrents(search_term: str) -> list:
    """Fetch torrent data asynchronously from Apibay."""
    params = {"q": search_term}
    async with httpx.AsyncClient() as client:
        response = await client.get(APIBAY_URL, params=params)
        response.raise_for_status()
        return response.json()

def sort_torrents_by_quality(torrents):
    quality_order = {'2160p': 1, '1080p': 2, '720p': 3, '480p': 4, 'Other': 5}
    def get_quality_order(torrent):
        for quality in quality_order.keys():
            if quality in torrent.get('quality', 'Other') or quality in torrent.get('name', 'Other'):
                return quality_order[quality]
        return quality_order['Other']
    return sorted(torrents, key=get_quality_order)

async def search_and_display_torrents(imdb_id: str):
    """Search for torrents by IMDb ID, exclude torrents with 0 seeders, and display the rest."""
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

    sorted_torrents = sort_torrents_by_quality(torrents_with_seeders)

    if not sorted_torrents:
        print(f"No torrents with seeders found for '{search_term.replace('+', ' ')}'.")
        return

    print(f"Found {len(sorted_torrents)} torrents with seeders for '{search_term.replace('+', ' ')}':")
    print()
    for torrent in sorted_torrents:
        title = torrent.get('name')
        magnet_link = f"magnet:?xt=urn:btih:{torrent.get('info_hash')}&dn={title.replace(' ', '+')}"
        seeders = torrent.get('seeders', 'N/A')
        print(f"Title: {title}\nMagnet: {magnet_link}\nSeeders: {seeders}\n")

async def main():
    await search_and_display_torrents(IMDB_ID)

if __name__ == "__main__":
    asyncio.run(main())