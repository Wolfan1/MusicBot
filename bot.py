#############
# Version: 9/15/2022
# Uses searchyoutube version: 9/15/2022
#############

import asyncio
import discord
import os
import platform
from discord.ext import commands
from datetime import datetime
from searchyoutube import youtube_search

operating_system = platform.system()

DISCORD_TOKEN = os.environ.get('DISCORD_BOT_TOKEN')

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix = '!', intents = intents)

@bot.event
async def on_ready():
    print("=====================================================")
    print(f"\nRunning on {operating_system}")
    print(f"\nLogged in as {bot.user} (ID: {bot.user.id})")
    print("\n=====================================================")

# Music-related commands
class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queue = []
        self.playing = None
        self.playing_msg = None

    # Join voice channel
    @commands.command(name='join', aliases=['j', 'J', 'Join'])
    async def join(self, ctx):
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        print("(" + current_time + ") " + str(ctx.author) + " used the command: " + str(ctx.message.content))

        if (ctx.author.voice):
            if ctx.voice_client == None:
                voice_channel = ctx.message.author.voice.channel
                await voice_channel.connect()
                await ctx.send("Joined " + str(voice_channel))
                print(" -Bot joined", str(voice_channel), "\n")
            else:
                await ctx.send("I'm already in a voice channel")
                print(" -Bot already in a voice channel\n")
        else:
            await ctx.send("You must be in a voice channel for me to join")
            print(" -User not in channel\n")

    # Leave voice channel
    @commands.command(name='leave', aliases=['l', 'L', 'Leave'])
    async def leave(self, ctx):
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        print("(" + current_time + ") " + str(ctx.author) + " used the command: " + str(ctx.message.content))

        if (ctx.voice_client):
            await ctx.guild.voice_client.disconnect()
            await ctx.send("I left the voice channel")
            print(" -Bot disconnected\n")
        else:
            await ctx.send("I'm not in a voice channel")
            print(" -Bot not in channel\n")

    # Play song
    @commands.command(name='play', aliases=['p', 'P', 'Play', 'add'])
    async def play(self, ctx):
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        print("(" + current_time + ") " + str(ctx.author) + " used the command: " + str(ctx.message.content))

        # Parse correct section of user message according to alias used
        search_query = ctx.message.content
        if search_query[1:5].upper() == 'PLAY':
            search_query = search_query[6:len(search_query)]
        elif search_query[1:4].upper() == 'ADD':
            search_query = search_query[5:len(search_query)]
        else:
            search_query = search_query[3:len(search_query)]

        # Check if the user in a channel
        if (ctx.author.voice):

            vc = ctx.voice_client

            # Check if the bot is already in a channel
            if vc == None:
                voice_channel = ctx.message.author.voice.channel
                vc = await voice_channel.connect()
                await ctx.send("Joined " + str(voice_channel))
                print(" -Bot joined " + str(voice_channel))
            else:
                pass

            # Search youtube and append result to queue
            audio_url, title, length, url = youtube_search(search_query)
            self.queue.append((title, audio_url, length, url))
            if not self.playing == None:    
                await ctx.send("Added \"**" + title + "**\" to queue")
            print(" -Added \"" + title + "\" to queue\n")

            # Begin playing songs, if not already
            if self.playing == None:
                await self.play_queue(ctx, vc)

        else:
            await ctx.send("You must be in a voice channel for me to join")
            print(" -User not in channel\n")

    async def play_queue(self, ctx, vc):

        # Continue going through queue while there are still songs in the queue
        while len(self.queue) != 0:

            # Retrieve and delete info about first song in queue
            title, audio_url, time, url = self.queue.pop(0)
            self.playing = title

            # Check OS to use proper ffmpeg
            # Begin playing audio from audio url
            if operating_system == "Windows":
                vc.play(discord.FFmpegPCMAudio(source=audio_url, executable="C:/FFmpeg/ffmpeg.exe"))
            elif operating_system == "Linux":
                vc.play(discord.FFmpegPCMAudio(source=audio_url))

            # Delete previous "Now playing" message
            """
            if not self.playing_msg == None:
                await self.playing_msg.delete()
                self.playing_msg = None
            """    
            
            # Send "Now playing" message
            self.playing_msg = await ctx.send("Now playing \"**" + title + "**\" (" + url + ")", delete_after=time)
            print(" -Bot began playing \"" + title + "\"\n")


            while vc.is_playing():
                await asyncio.sleep(.5)
        self.playing = None
        if self.playing_msg == None:
                pass
        else:
            await self.playing_msg.delete()

    @commands.command(name='queue', aliases=['q', 'Q', 'Queue'])
    async def queue(self, ctx):
        message = ""
        i = 1
        for tup in self.queue:
            time_seconds = tup[2]
            message += f"{i}: **{tup[0]}** *[{int(time_seconds/60)}:" + str(time_seconds%60).zfill(2) + "]*\n"
            i += 1
        await ctx.send(message)

    @commands.command(name='skip', aliases=['Skip'])
    async def skip(self, ctx):
        vc = ctx.voice_client
        if vc == None or not vc.is_playing():
            ctx.send("No song is currently playing")
            return
        vc.stop()
    
    @commands.command(name='playing', aliases=['Playing'])
    async def current(self, ctx):
        if self.playing == None:
            await ctx.send("No song is currently playing")
            print("No song is currently playing")
        else:
            await ctx.send(f"Currently playing {self.playing}")
            print(f"Currently playing {self.playing}")

    @commands.command(name='move', aliases=['Move'])
    async def move(self, ctx):
        def move_songs(frm:int, to:int):
            moving_item = self.queue[frm]
            self.queue.pop(frm)

            temp_list = self.queue[to:]
            #print(temp_list)

            for i in range(to, len(self.queue)):
                self.queue.pop(to)

            self.queue.append(moving_item)

            for i in temp_list:
                self.queue.append(i)

        words = []
        word = ""
        for char in ctx.message.content:
            if char == " ":
                words.append(word)
                word = ""
            else:
                word += char
        words.append(word)
        words.pop(0)

        if words[1].upper() == "TO":
            move_songs((int(words[0])-1), (int(words[2])-1))
            message = "New song order:\n"
            i = 1
            for tup in self.queue:
                time_seconds = tup[2]
                message += f"{i}: **{tup[0]}** *[{int(time_seconds/60)}:" + str(time_seconds%60).zfill(2) + "]*\n"
                i += 1
            await ctx.send(message)

        else:
            await ctx.send("Command must in the format \"!move [queue position] to [queue position]\"")

    @commands.command(name="remove", aliases=["Remove", "r"])
    async def remove(self, ctx):
        print(ctx.message.content[1:7].upper())
        if ctx.message.content[1:7].upper() == "REMOVE":
            self.queue.pop(int(ctx.message.content[8])-1)
        else:
            self.queue.pop(int(ctx.message.content[3])-1)





if __name__ == '__main__':
  bot.add_cog(Music(bot))
  bot.run(DISCORD_TOKEN)
