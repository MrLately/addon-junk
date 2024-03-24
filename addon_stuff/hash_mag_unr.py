import requests
import time


torrent_hash = "32ed4937042d85fe3b91e3fbbfaa102b183da00f"  # Example torrent hash
real_debrid_api_token = "TD362XKQPTUIHL25UIUYMUGQQ2PPFH5QHLLHFFBFACIUQ47E2C7Q"  # Your Real Debrid API token
headers = {"Authorization": f"Bearer {real_debrid_api_token}"}

def generate_magnet_link(hash):
    """Generate a magnet link from a torrent hash."""
    return f"magnet:?xt=urn:btih:{hash}"

def add_magnet_to_realdebrid(hash):
    """Send magnet link to Real-Debrid and return the torrent ID."""
    magnet = generate_magnet_link(hash)
    response = requests.post("https://api.real-debrid.com/rest/1.0/torrents/addMagnet", headers=headers, data={"magnet": magnet})
    response.raise_for_status()
    return response.json()['id']

def select_files_and_start_download(torrent_id):
    """Fetch torrent files, filter video files, select the largest video file, and start the download."""
    response = requests.get(f"https://api.real-debrid.com/rest/1.0/torrents/info/{torrent_id}", headers=headers)
    response.raise_for_status()
    files_info = response.json()['files']
    
    # Filter for video files and sort by size, descending (largest first)
    video_files = [file for file in files_info if file['path'].lower().endswith(('.mp4', '.mkv', '.avi', '.mov'))]
    if video_files:
        largest_video_file = sorted(video_files, key=lambda x: x['bytes'], reverse=True)[0]['id']
        response = requests.post(f"https://api.real-debrid.com/rest/1.0/torrents/selectFiles/{torrent_id}", headers=headers, data={"files": str(largest_video_file)})
        response.raise_for_status()
    else:
        print("No video files found in torrent.")

def check_download_status(torrent_id):
    """Check the status of the download and return the download link when ready."""
    while True:
        response = requests.get(f"https://api.real-debrid.com/rest/1.0/torrents/info/{torrent_id}", headers=headers)
        response.raise_for_status()
        torrent_info = response.json()
        if torrent_info['status'] == 'downloaded':
            download_link = torrent_info['links'][0]  # Assuming the first link is for the largest video file selected
            return download_link
        time.sleep(10)  # Check every 10 seconds

def unrestrict_link(download_link):
    """Convert a regular download link to a premium direct download link."""
    response = requests.post("https://api.real-debrid.com/rest/1.0/unrestrict/link", headers=headers, data={"link": download_link})
    response.raise_for_status()
    return response.json()['download']

def main():
    torrent_id = add_magnet_to_realdebrid(torrent_hash)
    print(f"Torrent hash added successfully, torrent ID: {torrent_id}")
    
    select_files_and_start_download(torrent_id)
    print("Largest video file in torrent selected and download started.")
    
    download_link = check_download_status(torrent_id)
    print(f"Download link obtained")
    
    unrestricted_link = unrestrict_link(download_link)
    print(f"Unrestricted Direct Download Link: {unrestricted_link}")

if __name__ == "__main__":
    main()

