from discord.ext import commands
from functions import Functions
from threading import Thread
from replit import db
import requests
import discord
import time
import os

version = '6.34.68'

'''
db['history'] = {0: ..., ...}
db['bio'] = str
db['prefix'] = str
db['config'] = {'mock': bool, ...}
db['ongoing_tasks'] = {task_id: [interval, message, channel], ...}
'''

# database
# db['history'] = {}
# db['logging'] = False
# db['bio'] = None
# db['prefix'] = '.'
# db['config'] = {'mock': True, 'reply': True, 'react': True, 'listener': True, 'mute': True}
# db['ongoing_tasks'] = {}

class Utility(commands.Cog):
  def __init__(self, client):
    self.client = client

  @commands.command()
  async def helpsb(self, ctx, cog=None):
    # automatically generates help files
    if db['hidden'] is True: await ctx.message.delete()
      
    if cog is None:
      await ctx.send(f'>>> Use `{self.client.command_prefix}helpsb {{cog}}` to view commands from a cog\n```'+'\n'.join([cog.replace('.py', '') for cog in os.listdir('./cogs')])+'```')
    else:
      if os.path.exists(f'cogs/{cog[0].upper()+cog[1:].lower()}.py'):
        commands = []
        with open(f'cogs/{cog[0].upper()+cog[1:].lower()}.py', 'r') as file:
          f = file.read().split('\n')
          for i, line in enumerate(f):
            if '@commands.command()' in line and not 'in line' in line:
              commands.append(f[i+1].replace('async def ', '').replace('self, ', '').replace('ctx, ', '').replace('ctx', '').replace(':', '').strip())
        await ctx.send('>>> ```'+'\n'.join(commands)+'```')

  @commands.command()
  async def debug(self, ctx):
    global version
    if db['hidden'] is True: await ctx.message.delete()
      
    lines = 0
    # add directories that contain .py files
    for dir in ['/home/runner/Devious-Selfbot-v6/', 'cogs/']:
      for file in os.listdir(dir):
        # check for python file
        if file.endswith('.py'):
          with open(f'{dir}{file}', 'r') as f:
            lines += len(f.read().split('\n'))
        else: continue


    commands = 0
    for file in os.listdir('cogs/'):
      if file.endswith('.py'):
        with open(f'cogs/{file}', 'r') as x:
          f = x.read().split('\n')
          for i, line in enumerate(f):
            if '@commands.command()' in line and not 'in line' in line:
              commands += 1

    await ctx.send(f'''>>> **Devious Selfbot**```
Version: {version}
Client: {self.client.user}
Latency: {round(self.client.latency, 3)} ms

Lines: {lines}
Commands: {commands}
Hidden: {db["hidden"]}  
Logging: {db["logging"]}
  
Last reboot: {round((time.time()-db["reboot"])/60/60, 2)} hours ago```''')

  @commands.command()
  async def avatar(self, ctx, user):
    if db['hidden'] is True: await ctx.message.delete()
    user = Functions.id_from_mention(user)

    member = await self.client.fetch_user(user)
    await ctx.send(member.avatar_url)

  @commands.command()
  async def info(self, ctx, user):
    if db['hidden'] is True: await ctx.message.delete()
    user = Functions.id_from_mention(user)

    created = await self.client.fetch_user(user)
    await ctx.send(f'>>> ```ID: {user}\nJoin Date: {created.created_at.strftime("%b %d, %Y")}```')

  @commands.command()
  async def viewsrc(self, ctx, index, lines=15, file_path='main.py'):
    if db['hidden'] is True: await ctx.message.delete()

    try:
      with open(file_path, 'r') as file:
        file = file.read().replace('```', '``').split('\n')
        try:
          for i, line in enumerate(file):
            if index in line: 
              section = file[i:i+lines]
              break
          await ctx.send('>>> ```py\n'+'\n'.join(section)+'```')
        except IndexError: pass
    except FileNotFoundError: pass

  @commands.command()
  async def reboot(self, ctx):
    if db['hidden'] is True: await ctx.message.delete()
      
    await ctx.send('||https://Devious-Selfbot-v6.cadenchau.repl.co||')
    os.system('kill 1')

  @commands.command()
  async def history(self, ctx, limit=5):
    if db['hidden'] is True: await ctx.message.delete()

    x = len(db['history'])
    for a in range(limit):
      items = []
      for item in list(db['history'].items())[x-10:x]:
        items.append(f'{item[0]}:\n\t{item[1].replace("```", "``")}')
      await ctx.send('>>> ```'+'\n'.join(items)+'```')
      x -= 10

  @commands.command()
  async def bio(self, ctx, keyword=None):
    if db['hidden'] is True: await ctx.message.delete()

    db['bio'] = keyword
    if not db['hidden'] is True:
      await ctx.send(f'>>> Set bio listener to **{keyword}**')

  @commands.command()
  async def prefix(self, ctx, prefix='.'):
    if db['hidden'] is True: await ctx.message.delete()

    db['prefix'] = prefix
    self.client.command_prefix = prefix
    if not db['hidden'] is True:
      await ctx.send(f'>>> Succesfully set prefix to **{prefix}**')

  @commands.command()
  async def config(self, ctx, setting=None, param=None):
    if db['hidden'] is True: await ctx.message.delete()

    if setting is None:
      await ctx.send(f'''>>> ```
Logging: {db['logging']}
Mock: {db['config']['mock']}
Reply: {db['config']['reply']}
React: {db['config']['react']}
Mute: {db['config']['mute']}
Listener: {db['config']['listener']}
```''')
    else:
      if setting.lower() in db['config'] or setting.lower() in db:
        if setting.lower() in ['logging']:
          db['logging'] = param.lower() in ['on']
        else:
          db['config'][setting.lower()] = param.lower() in ['on']
  
          if not db['hidden'] is True:
            await ctx.send(f'>>> Succesfully set config `{setting.lower()}` to **{param.lower() in ["on"]}**')

  @commands.command()
  async def quicksend(self, ctx, server=None, channel=None, *text):
    if db['hidden'] is True: await ctx.message.delete()

    server_list = [server for server in self.client.guilds]
    if server is None and channel is None:
      await ctx.send('>>> ```'+'\n'.join([f'{i+1}. {server.name}' for i, server in enumerate(server_list)])+'```')
    elif channel is None:
      channels = []
      for i, channel in enumerate(server_list[int(server)-1].channels):
        if str(channel.type) == 'text': channels.append(f'{i+1}. {channel.name}')
      await ctx.send('>>> ```'+'\n'.join(channels)+'```')
    elif not server is None and not channel is None:
      for i, chann in enumerate(server_list[int(server)-1].channels):
        if str(chann.type) == 'text':
          if i == int(channel)-1:
            channel_id = chann.id
            break
      Functions.send_message(channel_id, ' '.join(text))
      if not db['hidden'] is True:
        await ctx.send('>>> Sent message succesfully')

  @commands.command()
  async def task(self, ctx, interval, *message):
    if db['hidden'] is True: await ctx.message.delete()

    message = ' '.join(message)
    task_id = ctx.message.id
    times = {'h': 3600, 'm': 60, 's': 1}
    for t in times:
      if t in interval: 
        interval = int(interval.replace(t, ''))*times[t]
        break

    if not isinstance(ctx.message.channel, discord.channel.DMChannel):
      for chan in ctx.guild.channels:
        if chan.id == ctx.channel.id: channel_name = chan.name; break
    else: channel_name = 'DM Channel'

    if not db['hidden'] is True:
      await ctx.send(f'>>> Running task `{task_id}` on **{channel_name}**. Use `{self.client.command_prefix}viewtasks` to view running tasks')
    db['ongoing_tasks'][str(task_id)] = [interval, message, ctx.message.channel.id]
    Thread(target=lambda: Functions.run_task(str(task_id))).start()

  @commands.command()
  async def viewtasks(self, ctx):
    if db['hidden'] is True: await ctx.message.delete()

    if not db['ongoing_tasks'] == {}:
      await ctx.send('>>> ```'+'\n'.join([f'{task}:\n\t{db["ongoing_tasks"][task][0]}\n\t{db["ongoing_tasks"][task][1]}' for task in db['ongoing_tasks']])+'```')
    else:
      await ctx.send('>>> ```None```')
    
  @commands.command()
  async def endtask(self, ctx, task_id=None):
    if db['hidden'] is True: await ctx.message.delete()

    if task_id is None: 
      db['ongoing_tasks'] = {}
      if not db['hidden'] is True: 
        await ctx.send('>>> Succesfully cleared all tasks')
    else:
      try:
        del db['ongoing_tasks'][str(task_id)]
        await ctx.send(f'>>> Succesfully deleted task `{task_id}`')
      except KeyError: pass

  @commands.command()
  async def iconsteal(self, ctx):
    if db['hidden'] is True: await ctx.message.delete()

    try:
      await ctx.send(ctx.guild.icon_url)
    except: pass

  @commands.command()
  async def setav(self, ctx, url):
    if db['hidden'] is True: await ctx.message.delete()

    request = requests.get(url)
    with open('images/avatar_icon.png', 'wb') as file:
      file.write(request.content)
    with open('images/avatar_icon.png', 'rb') as image:
      await self.client.user.edit(password=os.environ['PASSWORD'], avatar=image.read())

      if not db['hidden'] is True:
        await ctx.send('>>> Succesfully updated profile')


def setup(client):
	client.add_cog(Utility(client))