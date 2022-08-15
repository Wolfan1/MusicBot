import keys
import asyncio
import discord
from discord.ext import commands
from datetime import datetime
from searchyoutube import youtube_search

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix = '!', intents = intents)

@bot.event
async def on_ready():
    print("=====================================================")
    print(f"\nLogged in as {bot.user} (ID: {bot.user.id})")
    print("\n=====================================================")

# Music-related commands
class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queue = []
        self.playing = None

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
    @commands.command(name='play', aliases=['p', 'P', 'Play'])
    async def play(self, ctx):
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        print("(" + current_time + ") " + str(ctx.author) + " used the command: " + str(ctx.message.content))

        choice = ctx.message.content
        if choice[1:5].upper() == 'PLAY':
            choice = choice[6:len(choice)]
        else:
            choice = choice[3:len(choice)]

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

            audio_url, title, length, url = youtube_search(choice)

            self.queue.append((title, audio_url, length, url))
            await ctx.send("Added \"" + title + "\" to queue")
            print(" -Added \"" + title + "\" to queue\n")

            if self.playing == None:
                await self.play_queue(ctx, vc)

            #print("Queue: " + str(self.queue))

        else:
            await ctx.send("You must be in a voice channel for me to join")
            print(" -User not in channel\n")

    async def play_queue(self, ctx, vc):
        while len(self.queue) != 0:
            title, audio_url, time, url = self.queue.pop(0)
            self.playing = title
            vc.play(discord.FFmpegPCMAudio(executable="C:/Users/colin/Documents/ffmpeg/bin/ffmpeg.exe", source=audio_url))
            await ctx.send("Now playing \"" + title + "\" (" + url + ")")
            print(" -Bot began playing \"" + title + "\"\n")
            while vc.is_playing():
                await asyncio.sleep(.5)
        self.playing = None

    @commands.command(name='queue', aliases=['q', 'Q', 'Queue'])
    async def queue(self, ctx):
        message = ""
        i = 1
        for tup in self.queue:
            message += f"{i}. {tup[3]}\n"
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


if __name__ == '__main__':
  bot.add_cog(Music(bot))
  bot.run(keys.DISCORD_TOKEN)