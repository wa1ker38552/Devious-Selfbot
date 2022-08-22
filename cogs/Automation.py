from discord.ext import commands
from functions import Functions
from replit import db
import requests


'''
db['mock'] = [str, ...]
db['reply'] = {str: msg, ...}
db['react'] = {str: [...], ...}
db['mute'] = [..., ]
'''

# Database
# db['mock'] = []
# db['hidden'] = False
# db['reply'] = {}
# db['react'] = {}
# db['mute'] = []

class Automation(commands.Cog):
  def __init__(self, client):
    self.client = client

  @commands.command()
  async def mock(self, ctx, user):
    if db['hidden'] is True: await ctx.message.delete()
    user = Functions.id_from_mention(user)

    if not str(user) in db['mock']:
      if user != self.client.user.id:
        db['mock'].append(str(user))

        if not db['hidden'] is True: await ctx.send(f'>>> Mocking: {await self.client.fetch_user(user)}')

  @commands.command()
  async def endmock(self, ctx, user):
    if db['hidden'] is True: await ctx.message.delete()
    user = Functions.id_from_mention(user)

    if str(user) in db['mock']:
      db['mock'].remove(str(user))

      if not db['hidden'] is True: await ctx.send(f'>>> Stopped mocking: {await self.client.fetch_user(user)}') 

  @commands.command()
  async def reply(self, ctx, user, *message):
    if db['hidden'] is True: await ctx.message.delete()
    user = Functions.id_from_mention(user)

    if not str(user) in db['reply']:
      if user != self.client.user.id:
        db['reply'][str(user)] = ' '.join(message)

        if not db['hidden'] is True: await ctx.send(f'>>> Replying to: {await self.client.fetch_user(user)}')

  @commands.command()
  async def endreply(self, ctx, user):
    if db['hidden'] is True: await ctx.message.delete()
    user = Functions.id_from_mention(user)

    if str(user) in db['reply']:
      del db['reply'][str(user)]

      if not db['hidden'] is True: await ctx.send(f'>>> Stopped replying to: {await self.client.fetch_user(user)}')

  @commands.command()
  async def react(self, ctx, user, *emojis):
    if db['hidden'] is True: await ctx.message.delete()
    user = Functions.id_from_mention(user)

    if not str(user) in db['react']:
      if user != self.client.user.id:
        db['react'][str(user)] = emojis

        if not db['hidden'] is True: await ctx.send(f'>>> Reacting to: {await self.client.fetch_user(user)} with {", ".join(emojis)}')

  @commands.command()
  async def endreact(self, ctx, user):
    if db['hidden'] is True: await ctx.message.delete()
    user = Functions.id_from_mention(user)

    if str(user) in db['react']:
      del db['react'][str(user)]

      if not db['hidden'] is True: await ctx.send(f'>>> Stopped reacting to: {await self.client.fetch_user(user)}')

  @commands.command()
  async def generatemail(self, ctx, count=1):
    if db['hidden'] is True: await ctx.message.delete()
    request = requests.get(f'https://www.1secmail.com/api/v1/?action=genRandomMailbox&count={count}')
    await ctx.send('>>> ```'+'\n'.join(request.json())+'```')

  @commands.command()
  async def checkmail(self, ctx, email):
    if db['hidden'] is True: await ctx.message.delete()
    login = email.split('@')[0]
    domain = email.split('@')[1]
    request = requests.get(f'https://www.1secmail.com/api/v1/?action=getMessages&login={login}&domain={domain}').json()

    if not request == []:
      for item in request:
        request = requests.get(f'https://www.1secmail.com/api/v1/?action=readMessage&login={login}&domain={domain}&id={item["id"]}').json()
        await ctx.send(f'>>> ```From: {item["from"]}\nSubject: {item["subject"]}\n\n\t{request["textBody"]}\n{item["date"]}```')

    else:
      await ctx.send('>>> ```Mailbox is empty!```')

  @commands.command()
  async def mute(self, ctx, user):
    if db['hidden'] is True: await ctx.message.delete()
      
    user = Functions.id_from_mention(user)

    if not str(user) in db['mute']:
      db['mute'].append(str(user))
      if not db['hidden'] is True:
        await ctx.send(f'>>> Muted user **{await self.client.fetch_user(user)}**')

  @commands.command()
  async def unmute(self, ctx, user=None):
    if db['hidden'] is True: await ctx.message.delete()

    if user is None:
      db['mute'] = []
      if not db['hidden'] is True:
        await ctx.send('>>> Succesfully cleared all mutes')
    else:
      user = Functions.id_from_mention(user)

      db['mute'].remove(str(user))
      if not db['hidden'] is True:
        await ctx.send(f'>>> Unmuted **{await self.client.fetch_user(user)}**')

def setup(client):
	client.add_cog(Automation(client))