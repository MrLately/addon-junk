import httpx
import asyncio

# Example IMDb ID
#IMDB_ID = 'tt0111161'  # The Shawshank Redemption
IMDB_ID = 'tt1136041'  # Cat's in the Bag s1e3 of Breaking Badd
OMDB_API_KEY = 'c93ebe7f'  # Replace with your actual OMDB API key
YTS_API_URL = "https://yts.mx/api/v2/list_movies.json"

async def fetch_movie_details_from_omdb(imdb_id: str) -> dict:
    """Fetch movie details using IMDb ID from OMDB API."""
    omdb_url = f"http://www.omdbapi.com/?i={imdb_id}&apikey={OMDB_API_KEY}"
    async with httpx.AsyncClient() as client:
        response = await client.get(omdb_url)
        response.raise_for_status()
        return response.json()

async def fetch_movie_torrents(imdb_id: str) -> dict:
    """Fetch movie torrents asynchronously from YTS.mx by IMDb ID."""
    params = {"query_term": imdb_id}
    async with httpx.AsyncClient() as client:
        response = await client.get(YTS_API_URL, params=params)
        response.raise_for_status()
        return response.json()

async def display_torrents_by_imdb_id(imdb_id: str):
    """Search for torrents by IMDb ID and display their details along with movie details from OMDB."""
    try:
        # Fetch and display movie details from OMDB
        omdb_data = await fetch_movie_details_from_omdb(imdb_id)
        print(f"Title: {omdb_data.get('Title')}, Year: {omdb_data.get('Year')}, Genre: {omdb_data.get('Genre')}")

        # Fetch and display torrents from YTS.mx
        yts_data = await fetch_movie_torrents(imdb_id)
        movies = yts_data.get("data", {}).get("movies", [])
        if not movies:
            print(f"No torrents found for IMDb ID {imdb_id}")
            return

        for movie in movies:
            print(f"Movie: {movie.get('title')} ({movie.get('year')})")
            for torrent in movie.get('torrents', []):
                print(f"Quality: {torrent.get('quality')}, Size: {torrent.get('size')}, URL: {torrent.get('url')}")
    except httpx.HTTPStatusError as e:
        print(f"HTTP error occurred: {e.response.status_code}")
    except Exception as e:
        print(f"An error occurred: {e}")

async def main():
    await display_torrents_by_imdb_id(IMDB_ID)

if __name__ == "__main__":
    asyncio.run(main())

