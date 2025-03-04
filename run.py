import os
import requests
import json
from urllib.parse import urljoin
from ast import literal_eval

# Set the base URL and the download directory
# Set the base URL and the download directory
BASE_URL = 'https://lsd.docking.org/api/targets'  # Replace with the actual base URL
DOWNLOAD_DIR = 'downloads'

# Create the download directory if it doesn't exist
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def download_file(url: str, save_path: str) -> None:
    """Downloads a file from a URL to the specified path."""
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(save_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        print(f'Downloaded: {save_path}')
    else:
        print(f'Failed to download: {url} (Status code: {response.status_code})')

def page_to_json(url: str):
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    return data

def process_url(url: str, current_dir: str = '') -> None:
    data = page_to_json(url)
    print("@ LSD")
    if isinstance(data, list):
        for item in data:
            if 'name' in item:
                name = item['name']
                
                DOWNLOAD_SUB_DIR = os.path.join(DOWNLOAD_DIR, current_dir, name)
                os.makedirs(DOWNLOAD_SUB_DIR, exist_ok=True)
                suburl = url.rstrip('/') + '/' + name
                sub_data = page_to_json(suburl)

                search_directory(suburl, sub_data, name, DOWNLOAD_SUB_DIR)
                
def search_directory(url: str, data: str, name: str, download_dir: str) -> None:
    """Processes a URL, navigating directories or downloading files based on the JSON response."""
    
    try:            
        if isinstance(data['contents'], list):
            print("> ", name)

            for sub_item in data['contents']:
                print(" - %s " %sub_item['type'], sub_item['name'])
                if 'directory' == sub_item['type']:
                    
                    proj_name = sub_item['name']
                    DOWNLOAD_SUB_DIR = os.path.join(download_dir, proj_name)
                    os.makedirs(DOWNLOAD_SUB_DIR, exist_ok=True)
                    
                    print("DOWNLOAD_SUB_DIR && GENERATE DIR ", DOWNLOAD_SUB_DIR)
                    print("download dir ", download_dir)
                    print("proj_name ", proj_name)

                    projurl = url.rstrip('/') + '/' + proj_name
                    print("sub dir ", projurl)
                    proj_data = page_to_json(projurl)
                    search_directory(projurl, proj_data, proj_name, DOWNLOAD_SUB_DIR)

                else:
                    # Download the file into the current directory
                    item_name = sub_item['name']
                    item_url = url.rstrip('/') + '/' + sub_item['name']
                    save_path = os.path.join(download_dir, item_name)
                    os.makedirs(os.path.dirname(save_path), exist_ok=True)
                    download_file(item_url, save_path)
        else:
            print(f'Unexpected JSON format at {url}')
    except requests.RequestException as e:
        print(f'Error accessing {url}: {e}')
    except json.JSONDecodeError as e:
        print(f'Error decoding JSON from {url}: {e}')

# Start processing from the base URL
process_url(BASE_URL)
