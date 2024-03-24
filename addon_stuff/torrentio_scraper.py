import httpx
import asyncio

VIDEO_ID = 'tt15822846'
CATALOG_TYPE = 'series'
SEASON = 1 
EPISODE = 1 
TORRENTIO_URL = "https://torrentio.strem.fun"
REAL_DEBRID_API_TOKEN = "TD362XKQPTUIHL25UIUYMUGQQ2PPFH5QHLLHFFBFACIUQ47E2C7Q"  # Insert your Real-Debrid API token here
headers = {"Authorization": f"Bearer {REAL_DEBRID_API_TOKEN}"}

async def fetch_stream_data(url: str) -> dict:
    """Fetch stream data asynchronously."""
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.json()

async def check_rd_cache(torrent_hash):
    api_url = f"https://api.real-debrid.com/rest/1.0/torrents/instantAvailability/{torrent_hash}"
    async with httpx.AsyncClient() as client:
        response = await client.get(api_url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        if torrent_hash in data and data[torrent_hash] and any(value for value in data[torrent_hash].values() if value):
            return "CACHED"
        else:
            return "NOT CACHED"

async def scrap_streams_from_torrentio(video_id: str, catalog_type: str, season: int = None, episode: int = None):
    """Get streams from Torrentio API."""
    if catalog_type == "series" and season is not None and episode is not None:
        url = f"{TORRENTIO_URL}/stream/{catalog_type}/{video_id}:{season}:{episode}.json"
    else:
        url = f"{TORRENTIO_URL}/stream/{catalog_type}/{video_id}.json"

    try:
        stream_data = await fetch_stream_data(url)
        streams = stream_data.get("streams", [])
        print(f"Found {len(streams)} streams for {catalog_type} ID {video_id}")

        # Prepare cache check tasks with title and hash
        cache_check_tasks = [(stream.get('title'), stream.get('infoHash'), check_rd_cache(stream.get('infoHash'))) for stream in streams]
        
        # Run cache check tasks concurrently
        results = await asyncio.gather(*[task[2] for task in cache_check_tasks])
        
        # Print results with cache status, including the hash
        for (title, info_hash, _), cache_status in zip(cache_check_tasks, results):
            print(f"Title: {title}\nInfoHash: {info_hash}\nCache Status: {cache_status}\n")
            
    except httpx.HTTPStatusError as e:
        print(f"HTTP error occurred: {e.response.status_code}")
    except Exception as e:
        print(f"An error occurred: {e}")

async def main():
    await scrap_streams_from_torrentio(VIDEO_ID, CATALOG_TYPE, SEASON, EPISODE)

if __name__ == "__main__":
    asyncio.run(main())





