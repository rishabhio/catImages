import os
import asyncio
import aiohttp
import aiofiles
import signal
import sys
import re
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

BASE_DIR = '.'  # Base directory to look for pages
API_KEY = os.getenv('CAT_API_KEY')  # Ensure your API key is set in the environment
if not API_KEY:
    logging.error("API_KEY environment variable is not set.")
    sys.exit(1)

# Update with the actual Cat API URL, replace the page number dynamically
API_URL_TEMPLATE = 'https://api.thecatapi.com/v1/images/search?limit=100&page={}'

# Variable to keep track of whether the process should continue running
running = True

def signal_handler(sig, frame):
    """Handle termination signals."""
    global running
    running = False
    logging.info("Stopping the process after current cycle...")

async def fetch_and_save_image(session, img_url, img_id, page_number):
    """Fetch and save the image content."""
    try:
        async with session.get(img_url) as response:
            if response.status == 200:
                image_content = await response.read()
                page_dir = f'page_{page_number}'
                os.makedirs(page_dir, exist_ok=True)  # Ensure the directory exists
                
                image_path = os.path.join(page_dir, f'{img_id}.jpg')
                
                try:
                    async with aiofiles.open(image_path, 'wb') as f:
                        await f.write(image_content)
                    logging.info(f"Downloaded and saved image {img_id}.jpg in {page_dir}")
                except Exception as e:
                    logging.error(f"Failed to save image {img_id}.jpg: {e}")
            else:
                logging.error(f"Failed to fetch image {img_id}: {response.status}")
    except aiohttp.ClientError as e:
        logging.error(f"HTTP error while fetching image {img_id}: {e}")
    except Exception as e:
        logging.error(f"Unexpected error while fetching image {img_id}: {e}")

async def fetch_page_content(session, page_number):
    """Fetch and process content from a specific page."""
    url = API_URL_TEMPLATE.format(page_number)
    headers = {'x-api-key': API_KEY}
    
    try:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                data = await response.json()  # Expecting a JSON response with image URLs and IDs
                tasks = []
                for item in data:
                    img_url = item['url']
                    img_id = item['id']
                    tasks.append(fetch_and_save_image(session, img_url, img_id, page_number))

                await asyncio.gather(*tasks)
            else:
                logging.error(f"Failed to fetch page {page_number}: {response.status}")
    except aiohttp.ClientError as e:
        logging.error(f"HTTP error for page {page_number}: {e}")
    except Exception as e:
        logging.error(f"Unexpected error while fetching page {page_number}: {e}")

async def download_pages(start_page):
    """Download pages starting from the specified page."""
    async with aiohttp.ClientSession() as session:
        page_number = start_page
        while running:
            await fetch_page_content(session, page_number)
            page_number += 1

def get_latest_page_number():
    """Get the highest page number from the directories."""
    max_page = -1
    for dirname in os.listdir(BASE_DIR):
        match = re.match(r'page_(\d+)', dirname)
        if match:
            try:
                page_number = int(match.group(1))
                max_page = max(max_page, page_number)
            except ValueError as e:
                logging.error(f"Failed to parse page number in {dirname}: {e}")
    return max_page

def main():
    """Main function to orchestrate downloading."""
    # Set up signal handler
    signal.signal(signal.SIGINT, signal_handler)

    # Get the largest page number
    latest_page_number = get_latest_page_number()
    start_page = latest_page_number + 1 if latest_page_number != -1 else 1

    logging.info(f"Starting to download from page {start_page}...")

    # Start downloading pages
    try:
        asyncio.run(download_pages(start_page))
    except Exception as e:
        logging.error(f"Unexpected error during the downloading process: {e}")

if __name__ == '__main__':
    main()
