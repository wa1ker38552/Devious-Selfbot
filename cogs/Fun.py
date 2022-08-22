from itertools import permutations as permutate
from youtube_search import YoutubeSearch
from discord.ext import commands
from functions import Functions
from replit import db
import requests
import random
import time


class Fun(commands.Cog):
  def __init__(self, client):
    self.client = client
    self.words = open('text_files/words.txt','r').read().split('\n')
    self.letters = list('abcdefghijklmnopqrstuvwxyz')
    
  @commands.command()
  async def wordscape(self, ctx, chars):
    if db['hidden'] is True: await ctx.message.delete()
      
    combination = list(chars)
    start_time = time.time()
    permutations, results = [], []

    for i in range(2, 6):
      permutations.extend(list(permutate(combination, i)))
    for index, permutation in enumerate(permutations):
      permutations[index] = ''.join(permutation)
    for permutation in permutations:
      if permutation in self.words:
        results.append(permutation)

    results = list(set(results))
    await ctx.send(f'>>> ```Results: {", ".join(results)}\nRuntime: {round(time.time()-start_time, 2)}s```')

  @commands.command()
  async def image(self, ctx, *query):
    if db['hidden'] is True: await ctx.message.delete()
      
    query = ' '.join(query)
    urls = Functions.query_image(query)

    if not urls == []:
      await ctx.send(random.choice(urls))

  @commands.command()
  async def comic(self, ctx):
    if db['hidden'] is True: await ctx.message.delete()
      
    request = requests.get('https://c.xkcd.com/random/comic/')
    url = Functions.find_index('Image URL (for hotlinking/embedding): <a href= "', '"', request.text)
    await ctx.send(url)

  @commands.command()
  async def youtube(self, ctx, *query):
    if db['hidden'] is True: await ctx.message.delete()

    query = ' '.join(query)
    result = YoutubeSearch(query, max_results=10).to_dict()
    results = []
    for item in result:
      results.append({
        'id': item['id'],
        'title': item['title'],
        'channel': item['channel'],
        'length': item['duration'],
        'views': item['views'],
        'published': item['publish_time']
      })
  
    picked = random.choice(results)
    await ctx.send(f'''>>> ```
{picked["title"]}
{picked["channel"]} 
  
Views: {picked["views"]} 
Length: {picked["length"]}  
Published: {picked["published"]}``` 
||https://www.youtube.com/watch?v={picked["id"]}||''')

  @commands.command()
  async def pypi(self, ctx, query, limit=10):
    if db['hidden'] is True: await ctx.message.delete()

    results = Functions.query_package(query)
    items = []
    for item in results[:limit]:
      items.append(f'| {item[0]} |\n\t{item[2]}\n\t{item[1]}')
    await ctx.send(f'>>> Showing **{limit}** results for **{query}** ```'+'\n'.join(items)+'```')

  @commands.command()
  async def calc(self, ctx, equation):
    if db['hidden'] is True: await ctx.message.delete()

    try:
      await ctx.send(f'>>> `{eval(equation)}`')
    except:
      await ctx.send('>>> Unable to evaluate equation')

  @commands.command()
  async def reddit(self, ctx, subreddit):
    if db['hidden'] is True: await ctx.message.delete()

    request = requests.get(f'https://reddit.com/r/{subreddit}/random.json', headers={'User-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'}).json()
    await ctx.send(request[0]["data"]["children"][0]["data"]["url"])

  @commands.command()
  async def eval(self, ctx, *code): # moved to main
    if db['hidden'] is True: await ctx.message.delete()

    # depricated until I can figure out how to do it without passing it into params
    # I really don't want to put it into main.py since the auto help page gen won't catch it...

  @commands.command()
  async def charreact(self, ctx, text):
    if db['hidden'] is True: await ctx.message.delete()
      
    if ctx.message.reference is not None:
      emojis = open('text_files/emoji_characters.txt', 'r').read().split('\n')
      
      # message history workaround
      async for message in ctx.message.channel.history(limit=100):
        if message.id == ctx.message.reference.message_id:
          for char in text.lower():
            await message.add_reaction(emojis[self.letters.index(char)])
          break

  @commands.command()
  async def animate(self, ctx, *text):
    text = ' '.join(text)
    cached_text = []
      
    time.sleep(0.5)
    for index, char in enumerate(text):
      cached_text.append(char)
      await ctx.message.edit(content=''.join(cached_text))
      time.sleep(0.2)

  
def setup(client):
	client.add_cog(Fun(client))