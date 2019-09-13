import discord
import random

client = discord.Client()

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    if message.content.startswith('bot'):
        #print(message.content)
        #print(message.content.__contains__(' -h'))
        await message.channel.send('Bot called!')
       
        # COMMAND INTERPRETATION 
        if message.content.__contains__(' -h') or message.content.__contains__('--help'):
            await message.channel.send('*HELP PAGE:*')
            await message.channel.send('-d | --dice : Roll a six-sided die.')
            await message.channel.send('-h | --help : You\'re looking at it...')

        if message.content.__contains__('-d') or message.content.__contains__('--dice'):
            # Roll a die
            await message.channel.send("You rolled a " + str(random.choice(range(1,7))) + "!")

client.run('NjE4NjI1OTk4NzI4MDY5MTMw.XW8aew.0H8Z5YmWrfrZ_qThQ7w0ZbiQf2I')
