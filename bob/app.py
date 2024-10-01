import requests 
response = requests.get('https://api.thecatapi.com/v1/images/search?limit=10')
data = response.json()

for item in data:
    url = item['url']
    image_res = requests.get(url)
    image_id = item['id']
    image_content = image_res.content 
    img_file = open(f'{image_id}.jpg', 'wb') 
    img_file.write(image_content)
    img_file.close()
