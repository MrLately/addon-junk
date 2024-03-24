import httpx
import asyncio

# Constants
IMDB_ID = 'tt0167260'  # The Lord of the Rings: The Return of the King
#IMDB_ID = 'tt1054725'  # Cat's in the Bag s1e3 of Breaking Bad
OMDB_API_KEY = 'c93ebe7f'  # Replace with your actual OMDB API key
YTS_API_URL = "https://yts.mx/api/v2/list_movies.json"
APIBAY_URL = "https://apibay.org/q.php"

# Fetch movie or series episode details using IMDb ID from OMDB API
async def fetch_movie_details_from_omdb(imdb_id: str) -> dict:
    omdb_url = f"http://www.omdbapi.com/?i={imdb_id}&apikey={OMDB_API_KEY}"
    async with httpx.AsyncClient() as client:
        response = await client.get(omdb_url)
        response.raise_for_status()
        return response.json()

# Fetch movie torrents asynchronously from YTS.mx by IMDb ID
async def fetch_movie_torrents(imdb_id: str) -> dict:
    params = {"query_term": imdb_id}
    async with httpx.AsyncClient() as client:
        response = await client.get(YTS_API_URL, params=params)
        response.raise_for_status()
        return response.json()

# Fetch title details using IMDb ID from OMDB API, handling both movies and series episodes
async def fetch_title_details(imdb_id: str) -> str:
    data = await fetch_movie_details_from_omdb(imdb_id)
    if data.get("Type") == "episode":
        series_id = data.get("seriesID")
        async with httpx.AsyncClient() as client:
            series_response = await client.get(f"http://www.omdbapi.com/?i={series_id}&apikey={OMDB_API_KEY}")
            series_data = series_response.json()
        series_title = series_data.get("Title", "").replace(" ", "+")
        season = data.get("Season", "").zfill(2)
        episode = data.get("Episode", "").zfill(2)
        search_term = f"{series_title}+S{season}E{episode}"
    else:
        search_term = data.get("Title", "").replace(" ", "+")
    return search_term

# Fetch torrent data asynchronously from Apibay
async def fetch_torrents_from_apibay(search_term: str) -> list:
    params = {"q": search_term}
    async with httpx.AsyncClient() as client:
        response = await client.get(APIBAY_URL, params=params)
        response.raise_for_status()
        return response.json()

# Display OMDB movie details
def display_omdb_details(omdb_data: dict):
    print("\nOMDB Movie Details")
    print("===================")
    title = omdb_data.get('Title', 'N/A')
    year = omdb_data.get('Year', 'N/A')
    genre = omdb_data.get('Genre', 'N/A')
    print(f"Title: {title}\nYear: {year}\nGenre: {genre}\n")

def sort_torrents_by_quality(torrents):
    quality_order = {'2160p': 1, '1080p': 2, '720p': 3, '480p': 4, 'Other': 5}
    def get_quality_order(torrent):
        for quality in quality_order.keys():
            if quality in torrent.get('quality', 'Other') or quality in torrent.get('name', 'Other'):
                return quality_order[quality]
        return quality_order['Other']
    return sorted(torrents, key=get_quality_order)

def display_yts_torrents(yts_data: dict, imdb_id: str):
    movies = yts_data.get("data", {}).get("movies", [])
    if not movies:
        print(f"\nNo torrents found for '{imdb_id}' from YTS.mx")
        return
    movie_title = movies[0].get('title') if movies else imdb_id
    total_torrents_count = sum(len(movie.get('torrents', [])) for movie in movies)  # Calculate total number of torrents across all movies
    print(f"\nFound {total_torrents_count} torrents for '{movie_title}' from YTS.mx:")
    print("====================================================================")
    for movie in movies:
        sorted_torrents = sort_torrents_by_quality(movie.get('torrents', []))
        for torrent in sorted_torrents:
            print(f"  Quality: {torrent.get('quality')}, Size: {torrent.get('size')}, URL: {torrent.get('url')}")

def display_apibay_torrents(torrents: list, search_term: str):
    if not torrents:
        print(f"\nNo torrents found for '{search_term.replace('+', ' ')}' from Apibay\n")
        return
    sorted_torrents = sort_torrents_by_quality(torrents)
    print(f"\nFound {len(sorted_torrents)} torrents for '{search_term.replace('+', ' ')}' from Apibay:")
    print("================================================================================")
    for torrent in sorted_torrents:
        title_display = torrent.get('name').replace(' ', '.')
        magnet_link = f"magnet:?xt=urn:btih:{torrent.get('info_hash')}&dn={title_display}"
        seeders = torrent.get('seeders', 'N/A')  # Assuming 'seeders' is the field name
        print(f"Title: {title_display}\n  Magnet: {magnet_link}\n  Seeders: {seeders}\n")

async def display_combined_torrent_results(imdb_id: str):
    omdb_data = await fetch_movie_details_from_omdb(imdb_id)
    display_omdb_details(omdb_data)
    
    yts_data = await fetch_movie_torrents(imdb_id)
    display_yts_torrents(yts_data, imdb_id)  # Pass IMDb ID here

    search_term = await fetch_title_details(imdb_id)
    apibay_torrents = await fetch_torrents_from_apibay(search_term)
    display_apibay_torrents(apibay_torrents, search_term)

# Main function
async def main():
    await display_combined_torrent_results(IMDB_ID)

# Entry point
if __name__ == "__main__":
    asyncio.run(main())

