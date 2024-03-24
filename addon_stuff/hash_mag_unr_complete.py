import requests
import time

torrent_hash = "32ed4937042d85fe3b91e3fbbfaa102b183da00f"  # Example torrent hash
real_debrid_api_token = "TD362XKQPTUIHL25UIUYMUGQQ2PPFH5QHLLHFFBFACIUQ47E2C7Q"
headers = {"Authorization": f"Bearer {real_debrid_api_token}"}
CURRENT_SEASON = 1  # if filled the torrent is a series if 0 its a movie
CURRENT_EPISODE = 1  # if filled the torrent is a series if 0 its a movie
excluded_dirs = ["featurettes", "deleted scenes", "specials", "sample", "extras", "bonus", "interviews", "trailers", "ost"]

def generate_magnet_link(hash):
    return f"magnet:?xt=urn:btih:{hash}"

def add_magnet_to_realdebrid(hash):
    magnet = generate_magnet_link(hash)
    response = requests.post("https://api.real-debrid.com/rest/1.0/torrents/addMagnet", headers=headers, data={"magnet": magnet})
    response.raise_for_status()
    return response.json()['id']

def filter_files(files_info):
    # Filter out files based on excluded directories and file type
    return [file for file in files_info if file['path'].lower().endswith(('.mp4', '.mkv', '.avi', '.mov'))
            and not any(excluded_dir in file['path'].lower() for excluded_dir in excluded_dirs)]

def select_largest_file_and_start_download(torrent_id):
    response = requests.get(f"https://api.real-debrid.com/rest/1.0/torrents/info/{torrent_id}", headers=headers)
    response.raise_for_status()
    files_info = response.json()['files']

    video_files = filter_files(files_info)
    if video_files:
        largest_video_file = sorted(video_files, key=lambda x: x['bytes'], reverse=True)[0]['id']
        response = requests.post(f"https://api.real-debrid.com/rest/1.0/torrents/selectFiles/{torrent_id}", headers=headers, data={"files": str(largest_video_file)})
        response.raise_for_status()
    else:
        print("No video files found in torrent.")

def select_all_video_files_and_start_download(torrent_id): 
    response = requests.get(f"https://api.real-debrid.com/rest/1.0/torrents/info/{torrent_id}", headers=headers)
    response.raise_for_status()
    files_info = response.json()['files']
    
    video_files = filter_files(files_info)
    if video_files:
        video_file_ids = [str(file['id']) for file in video_files]
        selected_files = ",".join(video_file_ids)
        
        response = requests.post(f"https://api.real-debrid.com/rest/1.0/torrents/selectFiles/{torrent_id}", headers=headers, data={"files": selected_files})
        response.raise_for_status()
    else:
        print("No video files found in torrent.")

def check_download_status(torrent_id):
    while True:
        response = requests.get(f"https://api.real-debrid.com/rest/1.0/torrents/info/{torrent_id}", headers=headers)
        response.raise_for_status()
        torrent_info = response.json()
        if torrent_info['status'] == 'downloaded':
            return torrent_info['links']
        time.sleep(10)

def unrestrict_links(download_links):
    unrestricted_links_with_details = []
    for download_link in download_links:
        response = requests.post("https://api.real-debrid.com/rest/1.0/unrestrict/link", headers=headers, data={"link": download_link})
        if response.status_code == 200:
            unrestricted_link_detail = response.json()
            unrestricted_links_with_details.append(unrestricted_link_detail)
        else:
            print(f"Error unrestricting link: {response.text}")

    # Assuming 'unrestricted_links_with_details' now contains a list of dictionaries with 'download' and possibly 'filename' keys
    return unrestricted_links_with_details

def filter_and_delete_non_matching_links(unrestricted_links_with_details):
    season_episode_str = f"s{CURRENT_SEASON:02}e{CURRENT_EPISODE:02}".lower()
    matching_link = None

    for link_detail in unrestricted_links_with_details:
        if season_episode_str in link_detail['filename'].lower():
            matching_link = link_detail['download']
            break

    if matching_link:
        # Optionally, delete non-matching downloads here if you have the IDs and access to an API endpoint for deletion
        print(f"Matching link found and kept: {matching_link}")
        return matching_link
    else:
        print("No matching link found.")
        return None

def main():
    download_all_files = CURRENT_SEASON != 0 and CURRENT_EPISODE != 0
    torrent_id = add_magnet_to_realdebrid(torrent_hash)
    print(f"Torrent hash added successfully, torrent ID: {torrent_id}")

    if download_all_files:
        select_all_video_files_and_start_download(torrent_id)
    else:
        select_largest_file_and_start_download(torrent_id)

    print("Selected files based on criteria and download started.")
    download_links = check_download_status(torrent_id)
    print("Download link(s) obtained, getting unrestricted links.")
    unrestricted_links_with_details = unrestrict_links(download_links)
    matching_link = filter_and_delete_non_matching_links(unrestricted_links_with_details)
    if matching_link:
        print(f"Unrestricted Direct Download Link: {matching_link}")
    else:
        print("Failed to find a matching unrestricted link.")

if __name__ == "__main__":
    main()

