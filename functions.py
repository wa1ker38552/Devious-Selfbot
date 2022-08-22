from bs4 import BeautifulSoup
from PIL import ImageFont
from PIL import ImageDraw
from replit import db
from PIL import Image
import requests
import json
import time
import sys
import re
import os
import io


class Functions:
  def id_from_mention(user) -> int:
    return int(user.replace('<', '').replace('>', '').replace('@', ''))

  def filter(orig, prefix):
    banned = open('text_files/blacklist.txt','r').read().split('\n')

    if not orig.startswith(prefix):
      text = orig.lower().split()
      for w1 in banned:
        if w1 in text: return '🚨 NO SWEARING !! 🚨'
        for w2 in text:
          if w1 in ''.join(list(set(list(w2)))): return '🚨 NO SWEARING !! 🚨'  
          else: break
      return orig
    else: return 'Command prefix detected!'

  def update_bio(message):
    headers = {'authorization': os.environ['AUTH_TOKEN'], 'content-type': 'application/json'}
    json = {'bio': message}
    requests.patch('https://discord.com/api/v9/users/@me', headers=headers, json=json)

  def check_bio(author, msg):
    if db['bio'].lower() in msg.lower():
      Functions.update_bio(f'{author.split("#")[0]}: `{msg.replace("`", "")}`')
      
  def send_message(channel_id, message):
    headers = {'authorization': os.environ['AUTH_TOKEN'], 'content-type': 'application/json'}
    json = {'content': message}
    request = requests.post(f'https://discord.com/api/v9/channels/{channel_id}/messages', headers=headers, json=json)
    return request.json()['id']

  def delete_message(channel_id, message_id):
    headers = {'authorization': os.environ['AUTH_TOKEN'], 'content-type': 'application/json'} 
    requests.delete(f'https://discord.com/api/v9/channels/{channel_id}/messages/{message_id}', headers=headers)

  def run_task(task_id):
    while True:
      try:
        Functions.send_message(db['ongoing_tasks'][task_id][2], db['ongoing_tasks'][task_id][1])
        time.sleep(db['ongoing_tasks'][task_id][0])
      except KeyError: break

  def create_thread(channel_id, name):
    headers = {"content-type": "application/json", "Authorization": os.environ['AUTH_TOKEN']}
    json = {"name": name, "type": 11, "auto_archive_duration": 10080, 'location': 'Message'}
    request = requests.post(f"https://discord.com/api/v9/channels/{channel_id}/threads", headers=headers, json=json)
    
    if request.status_code == 429:
      print(f'Failed {request.json()["retry_after"]}')
      time.sleep(request.json()['retry_after'])
      requests.post(f"https://discord.com/api/v9/channels/{channel_id}/threads", headers=headers, json=json)
    return request.status_code

  def discord_fake(url, name, message):
    with open('images/discordfake/avatar.png', 'wb') as file:
      request = requests.get(url)
      file.write(request.content)
  
    # resize profile
    Image.open('images/discordfake/avatar.png').resize((42, 42)).save('images/discordfake/avatar.png')
  
    # edit profile onto image
    background = Image.open("images/discordfake/discord_template.png")
    foreground = Image.open("images/discordfake/avatar.png")
    
    background.paste(foreground, (8, 11))
    background.save('images/discordfake/avatar_offset.png')
    
    background = Image.open("images/discordfake/avatar_offset.png")
    foreground = Image.open("images/discordfake/discord_template.png")
    
    background.paste(foreground, (0, 0), foreground)
    background.save('images/discordfake/final.png')
    
    original = Image.open('images/discordfake/final.png')
    font1 = ImageFont.truetype('images/discordfake/asimov.otf', 15)
    font2 = ImageFont.truetype('images/discordfake/whitney.otf', 18)
    
    # add text
    im = ImageDraw.Draw(original)
    im.text((70, 13), name, font=font1, fill=(255, 255, 255))
    im.text((70, 33), ' '.join(message), font=font2, fill=(255, 255, 255))
    original.save('images/discordfake/final.png')
    
    # add timestamp
    background = Image.open("images/discordfake/final.png")
    foreground = Image.open("images/discordfake/timestamp.png")
  
    L = len(name)*10 if not name.isupper() else len(name)*15
    background.paste(foreground, (68+L, 9))
    background.save('images/discordfake/final.png')

  def query_image(query):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36"}
    
    params = {"q": query, "tbm": "isch", "hl": "en", "ijn": "0"}
  
    html = requests.get("https://www.google.com/search", params=params, headers=headers, timeout=30)
    soup = BeautifulSoup(html.text, 'lxml')
  
    all_script_tags = soup.select('script')
    matched_images_data = ''.join(re.findall(r"AF_initDataCallback\(([^<]+)\);", str(all_script_tags)))
    matched_images_data_fix = json.dumps(matched_images_data)
    matched_images_data_json = json.loads(matched_images_data_fix)
    matched_google_image_data = re.findall(r'\[\"GRID_STATE0\",null,\[\[1,\[0,\".*?\",(.*),\"All\",', matched_images_data_json)
  
    removed_matched_google_images_thumbnails = re.sub(
          r'\[\"(https\:\/\/encrypted-tbn0\.gstatic\.com\/images\?.*?)\",\d+,\d+\]', '', str(matched_google_image_data))
  
    matched_google_full_resolution_images = re.findall(r"(?:'|,),\[\"(https:|http.*?)\",\d+,\d+\]",
                                                         removed_matched_google_images_thumbnails)
  
    images = []
    for index, fixed_full_res_image in enumerate(matched_google_full_resolution_images):
      original_size_img_not_fixed = bytes(fixed_full_res_image, 'ascii').decode('unicode-escape')
      original_size_img = bytes(original_size_img_not_fixed, 'ascii').decode('unicode-escape')
      images.append(original_size_img)
  
    return images

  def find_index(s, i, t):
    x = start = t.index(s)+len(s)
    while t[x] != i: x += 1
    return t[start:x]

  def query_package(query):
    response = requests.get(f'https://pypi.org/search/?q={query}')
  
    soup = BeautifulSoup(response.text, 'html.parser')
    unparsed_results = soup.find_all("a", attrs = {"class":"package-snippet"})
    results = []
    for item in unparsed_results:
      name = Functions.find_index('<span class="package-snippet__name">', '<', str(item).split('\n')[2])
      desc = Functions.find_index('<p class="package-snippet__description">', '<', str(item).split('\n')[8])
      link = Functions.find_index('<a class="package-snippet" href="', '"', str(item).split('\n')[0])
      results.append([name, f'pypi.org{link}', desc])
    return results

  def run_script(script):
    old_stdout = sys.stdout
    sys.stdout = buffer = io.StringIO()
  
    with open('script.py', 'w') as file:
      file.write(script)
    try:
      exec(open('script.py', 'r').read())  
      sys.stdout = old_stdout
      prevPrint = buffer.getvalue()
      return (f'```{prevPrint}```')
    except Exception as error:
      return (f'```diff\n-{error}```')

  def ack(channel_id, message_id):
    headers = {'Authorization': os.environ['AUTH_TOKEN'], 
               'cookie': os.environ['TOKEN'],
               "content-type": "application/json",
               'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36'}
    r = requests.post(f'https://discord.com/api/v9/channels/{channel_id}/messages/{message_id}/ack', headers=headers)
    print(r.status_code)
    print(r.json())