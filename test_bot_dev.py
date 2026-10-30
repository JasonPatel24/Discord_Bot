import discord
import random
import re
import pafy
import youtube_dl
import asyncio
import glob
import os
import http.client

FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

YDL_OPTIONS = {'format': 'bestaudio/best', 'noplaylist':'True'}


from discord.utils import get
from discord.ext import commands
from pytube import YouTube
from youtube_dl import YoutubeDL

from time import sleep

client = commands.Bot(command_prefix = "!")

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

# Represents the bot's connection to a voice chat
voice = None
currentRoll = 0

# Boolean tracker for whether or not a song needs to be looped
toLoop = False

@client.command(pass_context=True)
async def loop(ctx):
    global toLoop
    toLoop = not toLoop
    
    await ctx.message.channel.send(toLoop)
    
    if toLoop:
        await ctx.message.channel.send("Looping most recent song!")
        
    else:
        await ctx.message.channel.send("Looping disabled")
        

# QUESTIONS: 
# - What if we just keep it one-to-one? 
# - i.e. (1 above-average requires 1 below average, 1 slightly above needs 1 slightly below)
@client.command(pass_context=True)
async def distStats(ctx, highStats, floor, ceil):
    choices = (int(ceil) - int(floor)) + 1
    if (choices % 4) != 0:
        await ctx.message.channel.send("Not enough choices, lower floor, raise ceiling, or both.")
        
    else:
        if int(highStats) > 3:
            await ctx.message.channel.send("Too many strengths, maximum is 3.")
        
        else:
            if int(highStats) < 0:
                highStats = 0
                
            # Store stats in a string
            statStr = ""
            
            # Calculate spiky distributions:
            tier = choices / 4
            
            #print(int(highStats))
            
            for i in range(int(highStats)):
                highStat = int(floor) + int(3*tier)
                mod = random.choice(range(4))
                statStr += str(highStat + mod) + " "
                
                mod = random.choice(range(4))
                lowStat = int(floor) + mod
                statStr += str(lowStat) + " "
                
            # Calculate middle-distribution stats
            for j in range(3 - int(highStats)):
                midhighStat = int(floor) + int(2*tier)
                mod = random.choice(range(4))
                statStr += str(midhighStat + mod) + " "
                
                mod = random.choice(range(4))
                midlowStat = int(floor) + int(tier) + mod
                statStr += str(midlowStat) + " "
                
            await ctx.message.channel.send(statStr)
        
        
    
# Generates a random number from 1 to the number that is passed in
@client.command(pass_context=True)
async def roll(ctx, sides, silent=False):
    times = 1
    result = 0
    mod = 0
    
    if type(sides) is not int:
        if("+" in sides or "-" in sides) and re.search("[0-9]*$", sides) is not None:
            if "+" in sides:
                mod = int(re.search("[0-9]*$", sides)[0])
                
            elif "-" in sides:
                mod = -(int(re.search("[0-9]*$", sides)[0]))
            
            sides = re.sub('[0-9]*$', '', sides)
            sides = sides.replace("+", "")
            sides = sides.replace("-", "")
            
        if "d" in sides and re.search("^[0-9]*[^d]", sides) is not None:
            times = int(re.search("^[0-9]*[^d]", sides)[0])
            
        if "d" in sides:
            sides = int(re.search("[^d][0-9]*$", sides)[0])
    
    for i in range(1, times + 1):    
        roll = ""
        if ctx.message.author.name == "LegendarySummons":
            roll = str(random.choice(range(3 * (int(sides) // 4) + 1, int(sides) + 1))) #<--- Weighted rolls
            #roll = str(random.choice(range(int(sides), int(sides) + 1))) #<--- Max rolls
        else:    
            roll = str(random.choice(range(1,int(sides) + 1)))
        
        if times > 1:
            msg = "Roll " + str(i) + ": " + ctx.message.author.name + " rolled a " + roll
        
        else:
            msg = ctx.message.author.name + " rolled a " + str(int(roll) + mod) 
            
        # Keep track of the last number rolled
        global currentRoll
        currentRoll = int(roll)
        
        if silent == False: # For distinguishing between normal rolls and stat rolls
            # Add emotes based on roll results
            if (roll == '1'):
              msg += "... <:oof:655186849861599251>" # This is the Drifter OOF emoji.
            else:
              msg += "!"
      
            await ctx.message.channel.send(msg)
        
        result += int(roll)
    
    if times > 1 and silent == False:
        await ctx.message.channel.send("Total roll is " + str(result + mod))

# Make <times> rolls and get the highest number
@client.command(pass_context=True)
async def adv(ctx, sides, times="2"):
    highestRoll = 0
    
    for i in range(1, int(times) + 1):
        await ctx.message.channel.send('Roll '+str(i)+": ")
        await roll(ctx, sides)
        
        if currentRoll > highestRoll or highestRoll == 0:
            # DEBUG
            print(str(currentRoll) + " is higher than " + str(highestRoll))
            highestRoll = currentRoll
            
    await ctx.message.channel.send('Highest roll is **'+str(highestRoll)+'**!')
        
    # DEBUG
    print("Roll a d"+sides+" with x"+times+" advantage!")

# Make <times> rolls and get the lowest number
@client.command(pass_context=True)
async def disadv(ctx, sides, times="2"):
    lowestRoll = 0
    
    for i in range(1, int(times) + 1):
        await ctx.message.channel.send('Roll '+str(i)+": ")
        await roll(ctx, sides)
        
        if currentRoll < lowestRoll or lowestRoll == 0:
            # DEBUG
            print(str(currentRoll) + " is higher than " + str(lowestRoll))
            lowestRoll = currentRoll
            
    await ctx.message.channel.send('Lowest roll is **'+str(lowestRoll)+'**...')
        
    # DEBUG
    print("Roll a d"+sides+" with x"+times+" disadvantage!")
    
# Roll god stats for a character
async def godStats(ctx):
    dice = 4 # A stat roll is the aggregate of the 3 highest values from 4 dice rolls
    stats = 6 # A characater has six stats
    stat_die = 6 # Die for rolling stats is a d6
    rolls = [0] * dice
    
    maxStat = random.choice(range(0, stats))
    
    await ctx.message.channel.send('*Rolling stats...*')
    await ctx.message.channel.send('------------------')
        
    # Roll a value for each stat
    for stat in range(0, stats):
        lowestVal = 0 # Track the lowest roll
        statVal = 0 # Store the value for the whole stat
        
        #await ctx.message.channel.send('**=============== ROLLS FOR STAT '+str(stat + 1)+' ====================**')
        if stat == maxStat:
            trickDie = random.choice(range(0,dice))
            for die in range(dice):
                if die == trickDie:
                    await roll(ctx, stat_die, True)
                    statVal += currentRoll
                    rolls[die] = currentRoll
                    lowestVal = currentRoll
                else:
                    statVal += 6
                    rolls[die] = 6
        else:
            for die in range(dice):
                await roll(ctx, stat_die, True)
                statVal += currentRoll
                rolls[die] = currentRoll
                
                
                if currentRoll < lowestVal or lowestVal == 0:
                    lowestVal = currentRoll 
         
        #await ctx.message.channel.send('**==================================================**')
        
        #await ctx.message.channel.send('*Dropping lowest d6: '+str(lowestVal)+'*') # Inform the user of the lowest roll, which is being dropped from the stat total
        statVal -= lowestVal
        #await ctx.message.channel.send('**Stat '+str(stat+1)+": "+str(statVal)+'**')
        
        roll_breakdown = ""
        lowestPassed = False
        
        for r in rolls:
            if r == lowestVal and lowestPassed == False:
                roll_breakdown += "~~["+str(r)+"]~~ "
                lowestPassed = True
            else:
                roll_breakdown += "["+str(r)+"] "
                
        roll_breakdown.strip()
        roll_breakdown = roll_breakdown.replace(" ", "+")
        
        await ctx.message.channel.send('**Stat '+str(stat+1)+": " + roll_breakdown + " = " + str(statVal)+'**')
        
@client.command(pass_context=True)
async def draw(ctx):
    if ctx.message.author.name == "LegendarySummons":
        # if sun:
        #     await ctx.message.channel.send("LegendarySummons drew a King of Diamonds")
        # elif jester:
        #     await ctx.message.channel.send("LegendarySummons drew a Joker!")
        # elif star:
        #     await ctx.message.channel.send("LegendarySummons drew a Jack of Diamonds")
        # else:
        #     suits = ["Hearts", "Diamonds"]
        #     values = ["Ace", "Two", "Jack", "Queen", "King"]
            
        #    await ctx.message.channel.send("LegendarySummons drew a " + values[random.choice(range(0,len(values)))] + " of " + suits[random.choice(range(0,len(suits)))])
        override=True
        CARD = "Ten of Diamonds"
        if override:
            await ctx.message.channel.send(ctx.message.author.name + " drew a " + CARD)
        else:
            cards = [
                    'Two of Diamonds',
                    'Jack of Hearts',
                    'Queen of Hearts',
                    'Nine of Hearts',
                    'Three of Hearts',
                    'Seven of Hearts',
                    'Five of Hearts',
                    'Ten of Diamonds'
                ]
                
            await ctx.message.channel.send(ctx.message.author.name + " drew a " + cards[random.choice(range(0,len(cards)))])
    else:
        # suits = ["Hearts", "Diamonds", "Spades", "Clubs"]
        # values = ["Ace", "Two", "Jack", "Queen", "King"]
        
        # await ctx.message.channel.send(ctx.message.author.name + " drew a " + values[random.choice(range(0,len(values)))] + " of " + suits[random.choice(range(0,len(suits)))])
          cards = [
                'Two of Diamonds',
                'Jack of Hearts',
                'Queen of Hearts',
                'Nine of Hearts',
                'Three of Hearts',
                'Seven of Spades',
                'Seven of Hearts',
                'Five of Hearts',
                'Eight of Spades',
                'Five of Clubs',
                'Ten of Diamonds',
                'Jack of Clubs',
                'Nine of Spades',
            ]
        
          await ctx.message.channel.send(ctx.message.author.name + " drew a " + cards[random.choice(range(0,len(cards)))])

async def regularStats(ctx):
    dice = 4 # A stat roll is the aggregate of the 3 highest values from 4 dice rolls
    stats = 6 # A characater has six stats
    stat_die = 6 # Die for rolling stats is a d6
    rolls = [0] * dice
    
    maxStat = random.choice(range(0, stats))
    
    await ctx.message.channel.send('*Rolling stats...*')
    await ctx.message.channel.send('------------------')
        
    # Roll a value for each stat
    for stat in range(0, stats):
        lowestVal = 0 # Track the lowest roll
        statVal = 0 # Store the value for the whole stat
        
        #await ctx.message.channel.send('**=============== ROLLS FOR STAT '+str(stat + 1)+' ====================**')
        if stat == maxStat:
            trickDie = random.choice(range(0,dice))
            for die in range(dice):
                if die == trickDie:
                    await roll(ctx, stat_die, True)
                    statVal += currentRoll
                    rolls[die] = currentRoll
                    lowestVal = currentRoll
                else:
                    statVal += 6
                    rolls[die] = 6
        else:
            for die in range(dice):
                await roll(ctx, stat_die, True)
                statVal += currentRoll
                rolls[die] = currentRoll
                
                
                if currentRoll < lowestVal or lowestVal == 0:
                    lowestVal = currentRoll
        
        #await ctx.message.channel.send('**==================================================**')
        
        #await ctx.message.channel.send('*Dropping lowest d6: '+str(lowestVal)+'*') # Inform the user of the lowest roll, which is being dropped from the stat total
        statVal -= lowestVal
        #await ctx.message.channel.send('**Stat '+str(stat+1)+": "+str(statVal)+'**')
        
        roll_breakdown = ""
        lowestPassed = False
        
        for r in rolls:
            if r == lowestVal and lowestPassed == False:
                roll_breakdown += "~~["+str(r)+"]~~ "
                lowestPassed = True
            else:
                roll_breakdown += "["+str(r)+"] "
                
        roll_breakdown.strip()
        roll_breakdown = roll_breakdown.replace(" ", "+")
        
        await ctx.message.channel.send('**Stat '+str(stat+1)+": " + roll_breakdown + " = " + str(statVal)+'**')
        
# Roll stats for a character
@client.command(pass_context=True)
async def stats(ctx):
    if ctx.message.author.name == "LegendarySummons":
        await godStats(ctx)
    else:
        await regularStats(ctx)
        
# Generate a guide to all the bot's commands and display it in a text channel
@client.command(pass_context=True)
async def gethelp(ctx):
    await ctx.message.channel.send('*HELP PAGE:*')
    await ctx.message.channel.send('!roll <sides> : Roll a multiple-sided die, where "sides" is the number of sides on the die')
    await ctx.message.channel.send('!adv <sides> <times>: Roll a <sides>-sided die <times> times and take the highest number')
    await ctx.message.channel.send('!disadv <sides> <times>: Roll a <sides>-sided die <times> times and take the lowest number')
    await ctx.message.channel.send('!stats: Roll 4d6 for each of a character\'s six stats (lowest d6 roll is dropped for each stat)')
    await ctx.message.channel.send('!pause: Pauses song')
    await ctx.message.channel.send('!gethelp : You\'re looking at it...')
    await ctx.message.channel.send('!play <URL> : Play a song from a YouTube link (URL)')
    await ctx.message.channel.send('!pause: Pauses song')
    await ctx.message.channel.send('!resume: Resumes song')
    await ctx.message.channel.send('!stop: Stops playing music (will need another song to play)')
    await ctx.message.channel.send('!leave: Leaves voice call')
    await ctx.message.channel.send('!draw: Draw a card from the major figures (Ace, 2, Jack, Queen, King) from all four suits')
    
songs = [0]

@client.command(pass_context=True)
async def queue(ctx, url):
    songs.append(url)
    await ctx.message.channel.send('Your song has been queued!')
    
async def nextSong(ctx):
    songs.pop(0)

async def checkLoop(ctx, url, voice, e):
    print("Checking for loop!")
    global toLoop
    
    if toLoop and voice.is_playing() == False:
        #sleep(3)
        await playVideo(ctx, url)
    
# TODO: This function should only focus on playing songs from urls
async def playVideo(ctx, url):
    # PAFY not working at the time of this comment
    #video = pafy.new(url)
            
    #print("The video is called: " + video.title)
    
    # DEBUG
    #for s in video.audiostreams:
        #print(s)
        
    #print("The new file that will be downloaded is: "+video.title+"."+video.getbestaudio().extension)
        
    # Pafy download fails with '/' character in the file name (PAFY not working at the time of this comment)
    #video.getbestaudio().download(filepath="../music/"+video.title.replace('/', '-')+"."+video.getbestaudio().extension, quiet=False)
    
    # Pytube Code
    #os.system("rm *.mp4");
    #print("URL is: " + url)
    #print(type(ctx))
    #YouTube(url).streams.get_highest_resolution().download()
    #print("Download complete!")
    
    # Pytube Code
    print(url)
    
    channel = ctx.message.author.voice.channel
    global voice
    
    #voice = get(client.voice_clients, guild=ctx.guild)
    
    #voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice and voice.is_connected():
        await voice.move_to(channel)
        
    if voice and voice.is_playing() == True:
        await queue(ctx, url)
    
    else:
        print("Playing song!")
        print("Connected!")
        ydl = youtube_dl.YoutubeDL(YDL_OPTIONS)
        with ydl:
            info = ydl.extract_info(url, download=False)
            I_URL = info['formats'][0]['url']
            #print(I_URL)
            source = await discord.FFmpegOpusAudio.from_probe(I_URL, **FFMPEG_OPTIONS)
            #print("SOURCE IS " + type(source))
            voice.play(source)
            #voice.is_playing()
        #voice.play(discord.FFmpegPCMAudio('../music/'+video.title.replace('/', '-')+"."+video.getbestaudio().extension), after=lambda e: print('done', e))
        
        #list_of_files = glob.glob('./*.mp4') # . means current directory
        #latest_file = max(list_of_files, key=os.path.getctime)

        #voice.play(discord.FFmpegPCMAudio(latest_file), after=lambda e: checkLoop(ctx, url, voice, e))
        
        # while (await checkLoop() == True):
        #     if voice.is_playing() == False:
        #         voice.play(discord.FFmpegPCMAudio(latest_file), after=lambda e: print('done', e))
        
        # See if there are still songs to play
        # if len(songs) > 0:
        #     while voice.is_playing() == True: # THIS STOPS THE BOT FROM BEING USED WHILE SONGS ARE BEING PLAYED!!!! also creates problems
        #         pass
            
        #     #sleep(2000)
        #     print('Playing next song...')
        #     await nextSong(ctx)
        #     await playVideo(ctx, songs[0])
        
# Given a YouTube url, download the best audio stream and play the file in a voice channel

# TODO: 
# - If a user isn't connected to a voice chat, tell them to do so before using the play command
# - IMPLEMENT QUEUES
# - PLAYLISTS???
# - Add loop and repeat functions
@client.command(pass_context=True)
async def play(ctx, url):
    debug = True # Toggle this for debugging output
    
    if debug:
        print("Query is: " + url)
        
    domain = "youtube.com/watch?v="
    
    # If search term:
    if domain not in url and "youtu.be" not in url:
        print("It's a search term!")
        
        # Search query DEBUG
        #print(ctx.message.content.replace("!play ", ""))
        url = ctx.message.content.replace("!play ", "")
        
        # Get rid of spaces and special characters as this search term is going in a url
        url = url.replace(" ", "%20").replace("&", "%26").replace("'", "%27")
        print("Formatted URL: " + url)
        #exit()
        # Get the video id to append to 'youtube.com/watch?v='
        stream = os.popen("curl 'https://www.googleapis.com/youtube/v3/search?part=snippet&maxResults=25&q="+ url +"&key=AIzaSyCv5dPAkS6n77XrMWa3DCd6xuy2yaGF_t0' --header 'Accept: application/json' --compressed")
        output = stream.read()
        #print(type(output))
        
        #print("Returned output: " + output) # Only sees the first word of search term, need to capture everything after '!play'
        #print(output)
        
        videoID = re.search(r'\"videoId\": \"(.*)\"', output).group(1)
        url = domain + videoID
        
        # Preview song (send message)
        await ctx.message.channel.send("*Playing:* " + "https://" + url)
        
        # 'url' is 'domain' + the video id, which will be sent to pafy
        
    # If link:
    await playVideo(ctx, url)

# Pauses current player
@client.command(pass_context=True)
async def pause(ctx):
    voice.pause()

# Resumes current player    
@client.command(pass_context=True)
async def resume(ctx):
    voice.resume()
    
# Stops current player
@client.command(pass_context=True)
async def stop(ctx):
    voice.stop()

# Leaves a voice chat    
@client.command(pass_context=True)
async def leave(ctx):
    print("Bot leaving")
    await ctx.message.channel.send("*Ayt ima head out...*")
    voice_client = ctx.voice_client
    await voice.disconnect()

client.run('YOUR_BOT_TOKEN_HERE')