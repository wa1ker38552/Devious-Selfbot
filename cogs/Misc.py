from discord.ext import commands
from functions import Functions
from PIL import Image
from replit import db
import requests
import discord
import os


class Misc(commands.Cog):
  def __init__(self, client):
    self.client = client
    self.default_bio = 'i leik to code bots'

  @commands.command()
  async def mocking(self, ctx):
    if db['hidden'] is True: await ctx.message.delete()
    if not db['mock'] == []:
      await ctx.send('>>> ```'+'\n'.join([str(await self.client.fetch_user(user)) for user in db["mock"]])+'```')
    else:
      await ctx.send('>>> ```None```')     

  @commands.command()
  async def replying(self, ctx):
    if db['hidden'] is True: await ctx.message.delete()
    if not db['reply'] == {}:
      await ctx.send('>>> ```'+'\n'.join([str(await self.client.fetch_user(user)) for user in db["reply"]])+'```')
    else:
      await ctx.send('>>> ```None```')   

  @commands.command()
  async def reacting(self, ctx):
    if db['hidden'] is True: await ctx.message.delete()
    if not db['react'] == {}:
      items = []
      for item in db['react']:
        items.append(f'`{str(await self.client.fetch_user(item))}`: {", ".join(db["react"][item])}')
        
      await ctx.send('>>> '+'\n'.join(items))
    else:
      await ctx.send('>>> ```None```')  

  @commands.command()
  async def e(self, ctx, name):
    if os.path.exists(f'images/emojis/{name}.png'):
      file = discord.File(f'images/emojis/{name}.png')

      await ctx.message.delete()
      if ctx.message.reference is not None:
        async for message in ctx.message.channel.history(limit=100):
          if message.id == ctx.message.reference.message_id:
            await message.reply(file=file, mention_author=False)
      else:
        await ctx.send(file=file)

  @commands.command()
  async def emojis(self, ctx):
    if db['hidden'] is True: await ctx.message.delete()
    emojis = os.listdir('images/emojis/')
    items = []
    for i, emoji in enumerate(emojis):
      items.append(f'{i+1} | {emoji.replace(".png", "")}')
    if items == []:
      await ctx.send('>>> ```None```')
    else:
      await ctx.send('>>> ```'+'\n'.join(items)+'```')

  @commands.command()
  async def emoji(self, ctx, emoji, name):
    if db['hidden'] is True: await ctx.message.delete()
    emoji = emoji.split(':')[2][:-1]

    request = requests.get(f'https://cdn.discordapp.com/emojis/{emoji}.png?size=96&quality=lossless')
    with open(f'images/emojis/{name}.png', 'wb') as file:
      file.write(request.content)

    Image.open(f'images/emojis/{name}.png').resize((30, 30)).save(f'images/emojis/{name}.png')
    if not db['hidden'] is True:
      await ctx.send(f'>>> Succesfully copied over emoji to **{name}** from **{ctx.guild.name}**')

  @commands.command()
  async def delemoji(self, ctx, name):
    if db['hidden'] is True: await ctx.message.delete()
    if os.path.exists(f'images/emojis/{name}.png'):
      os.remove(f'images/emojis/{name}.png')
      await ctx.send(f'>>> Succesfully removed emoji **{name}**')

  @commands.command()
  async def viewdb(self, ctx, key=None):
    if db['hidden'] is True: await ctx.message.delete()

    if key is None:
      items = []
      for key in db:
        items.append(f'{key}:\n\t{type(db[key])}')
          
      await ctx.send('>>> ```'+'\n'.join(items)+'```')
    else:
      await ctx.send(f'>>> ```{db[key]}```')

  @commands.command()
  async def cleardb(self, ctx, key):
    if db['hidden'] is True: await ctx.message.delete()

    try:
      db[key].clear()
    except KeyError: pass

  @commands.command()
  async def hidden(self, ctx, on_off):
    if db['hidden'] is True: await ctx.message.delete()

    if on_off == 'on':
      await ctx.message.delete()
      db['hidden'] = True
      db['bio'] = None
      Functions.update_bio(self.default_bio)
    else:
      db['hidden'] = False
      await ctx.send('>>> Set hidden to **False**')

  @commands.command()
  async def muted(self, ctx):
    if db['hidden'] is True: await ctx.message.delete()

    if db['mute'] == []:
      await ctx.send('>>> ```None```')
    else:
      await ctx.send('>>> ```'+'\n'.join([str(await self.client.fetch_user(int(user))) for user in db['mute']])+'```')
    
    
def setup(client):
	client.add_cog(Misc(client))