from discord.ext import commands
from functions import Functions
from replit import db
import requests
import discord
import asyncio
import time
import os


class Trolling(commands.Cog):
  def __init__(self, client):
    self.client = client
    
  @commands.command()
  async def ghostping(self, ctx, user='@everyone'):
    await ctx.message.delete()

    # faster than using await loop
    Functions.delete_message(ctx.channel.id, Functions.send_message(ctx.channel.id, user))

  @commands.command()
  async def spamthreads(self, ctx, name, amount=20):
    await ctx.message.delete()

    for i in range(int(amount)):
      Functions.create_thread(ctx.message.channel.id, name)

  @commands.command()
  async def typing(self, ctx, seconds: int):
    await ctx.message.delete()

    if not db['hidden'] is True:
      await ctx.send(f'>>> Typing on channel {ctx.channel.id} for **{round(seconds/60/60)} hours**')
    async with ctx.channel.typing():
      await asyncio.sleep(seconds)

  @commands.command()
  async def massreact(self, ctx, emoji, limit=20):
    await ctx.message.delete()

    # removed self react since message is auto deleted
    c = 0
    async for message in ctx.channel.history(limit=100):
      if c == limit: break
      else:
        if message.author.id != self.client.user.id:
          await message.add_reaction(emoji)
          c += 1

  @commands.command()
  async def massadd(self, ctx, limit=10, *users):
    await ctx.message.delete()

    users = [Functions.id_from_mention(user) for user in users]
    users.append(self.client.user.id)

    headers= {'authorization': os.environ['AUTH_TOKEN'], 'content-type': 'application/json'}
    json = {'recipients': users}
    
    c = 0
    try:
      while not c == int(limit):
        request = requests.post(f'https://discord.com/api/v9/users/@me/channels', headers=headers, json=json)
        if request.status_code == 429:
          time.sleep(5)
        else:
          requests.delete(f'https://discord.com/api/v9/channels/{request.json()["id"]}?silent=true', headers=headers)
          time.sleep(0.5)
          c += 1
    except:
      await ctx.send(f'>>> `{request.json()}`')

  @commands.command()
  async def discordfake(self, ctx, user, *message): # depricated
    if db['hidden'] is True: await ctx.message.delete()

    url = await self.client.fetch_user(Functions.id_from_mention(user))
    url = url.avatar_url
    name = await self.client.fetch_user(Functions.id_from_mention(user))
    name = name.display_name
    
    Functions.discord_fake(url, name, ''.join(message))
    file = discord.File('images/discordfake/final.png')
    await ctx.send(file=file)
    
    
def setup(client):
	client.add_cog(Trolling(client))