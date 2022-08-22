from discord.ext import commands
from functions import Functions
from threading import Thread
from alive import keepAlive
from replit import db
import discord
import time
import os

client = commands.Bot(command_prefix=db['prefix'], self_bot=True, help_command=None)

for file in os.listdir('./cogs'):
  if file.endswith('.py'):
    client.load_extension('cogs.' + file[:-3])

@client.event
async def on_ready():
  print(client.user)
  db['reboot'] = time.time()

@client.event
async def on_message(message):
  if db['config']['listener'] is False:
    if message.author.id == client.user.id:
      if str(message.content).split('\n')[0] == f'{client.command_prefix}eval':
        script = str(message.content).replace(f'{client.command_prefix}eval', '').replace('```py', '').replace('```', '')
        await message.channel.send('>>> '+Functions.run_script(script))

  else:
    # intents workaround to retrieve messages
    try:
      async for message in message.channel.history(limit=1): msg = str(message.content)
    except: msg = str(message.content)
  
    if db['logging'] is True:
      db['history'][str(message.author)] = msg
  
    if db['bio'] != None:
      Thread(target=lambda: Functions.check_bio(str(message.author), msg)).start()    
      
    # process automated responses
    if db['config']['mute'] is True:
      if isinstance(message.channel, discord.channel.DMChannel):
        if str(message.author.id) in db['mute']:
          Functions.ack(message.channel.id, message.id)
      
    if db['config']['mock'] is True:
      if str(message.author.id) in db['mock']: 
        await message.channel.send(Functions.filter(msg, client.command_prefix))
  
    if db['config']['reply'] is True:
      if str(message.author.id) in db['reply']:
        await message.reply(db['reply'][str(message.author.id)], mention_author=False)
  
    if db['config']['react'] is True:
      if str(message.author.id) in db['react']:
        for emoji in db['react'][str(message.author.id)]:
          await message.add_reaction(emoji)
  
  # process command only if contains prefix
  if message.content.startswith(client.command_prefix):
    await client.process_commands(message)


keepAlive()
client.run(os.environ['TOKEN'], bot=False)