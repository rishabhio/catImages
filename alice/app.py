import requests 
import logging
import os
import threading 
import time 

logging.basicConfig(
    level=logging.DEBUG,                   
    format='%(asctime)s - %(levelname)s - %(message)s',  
    handlers=[
        logging.FileHandler('app.log'),      
        logging.StreamHandler()
    ]
)

def init_storage():
    if not os.path.exists(CAT_STORAGE):
        os.makedirs(CAT_STORAGE)

CAT_API_URL = 'https://api.thecatapi.com/v1/images/search?limit=10'
CAT_STORAGE = 'cat_images/'

def fetch_cat_image( cat_id, cat_url ):
    logging.info(f'Fetching image with id {cat_id}')
    image_res = requests.get(cat_url)
    image_id = cat_id 
    image_content = image_res.content 
    store_image(image_id, image_content)

def fetch_cat_images():
    logging.info(f'Starting Fetch Operation')
    response = requests.get(CAT_API_URL)
    data = response.json()
    threads = [ ] 
    for item in data:
        logging.info(f'Init thread for {item["id"]}')
        thread = threading.Thread(target=fetch_cat_image, args=(item['id'], item['url']))
        threads.append(thread)
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join() 
    logging.info(f'Finished Fetch Operation')


def store_image(image_id, image_content):
    logging.info(f'Storing image with id {image_id}')
    img_file = open(f'{CAT_STORAGE}{image_id}.jpg', 'wb') 
    img_file.write(image_content)
    img_file.close()

if __name__ == '__main__':
    logging.info(f'Starting to fetch cat images')
    start = time.time() 
    init_storage()
    fetch_cat_images()
    finish = time.time()
    print(f'Time: {finish - start}')