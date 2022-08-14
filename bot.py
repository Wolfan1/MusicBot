import asyncio
from time import sleep
import discord
from discord.ext import commands
from discord import FFmpegPCMAudio
import keys
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
class Voice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queue = []

    # Join voice channel
    @commands.command(name='join', aliases=['j', 'J', 'Join'])
    async def join(self, ctx):
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        print("(" + current_time + ") " + str(ctx.author) + " used the command: " + str(ctx.message.content))

        if (ctx.author.voice):
            if ctx.voice_client == None:
                voice_channel = ctx.message.author.voice.channel
                vc = await voice_channel.connect()
                await ctx.send("Joined " + str(voice_channel))
                print(" -Bot joined " + str(voice_channel) + "\n")
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

    # Play song
    @commands.command(name='play', aliases=['p', 'P', 'Play'])
    async def play(self, ctx):
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        print("(" + current_time + ") " + str(ctx.author) + " used the command: " + str(ctx.message.content))



        # Check if the user in a channel
        if (ctx.author.voice):

            vc = ctx.voice_client
            # Check if the bot is already in a channel
            if ctx.voice_client == None:
                voice_channel = ctx.message.author.voice.channel
                vc = await voice_channel.connect()
                await ctx.send("Joined " + str(voice_channel))
                print(" -Bot joined " + str(voice_channel))
            else:
                pass

            search_query = ctx.message.content[6:len(ctx.message.content)]
            audio_url, title, length, url = youtube_search(search_query)

            if not vc.is_playing():
                vc.play(discord.FFmpegPCMAudio(source=audio_url))
                await ctx.send("Now playing \"" + title + "\"")
                print(" -Bot began playing \"" + title + "\"\n")
                while vc.is_playing():
                    await asyncio.sleep(.5)
                await self.play_queue(ctx, vc)
            else:
                self.queue.append((title, audio_url, length, url))
                await ctx.send("Added \"" + title + "\" to queue")
                print(" -Added \"" + title + "\" to queue\n")
                #print("Queue: " + str(self.queue))

        else:
            await ctx.send("You must be in a voice channel for me to join")
            print(" -User not in channel\n")

    async def play_queue(self, ctx, vc):
        if len(self.queue) == 0:
            return
        title, audio_url, time, url = self.queue.pop(0)
        vc.play(discord.FFmpegPCMAudio(source=audio_url))
        await ctx.send("Now playing \"" + title + "\" (" + url + ")")
        print(" -Bot began playing \"" + title + "\"\n")
        while vc.is_playing():
            await asyncio.sleep(.5)
        await self.play_queue(ctx, vc)

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

            



bot.add_cog(Voice(bot))
bot.run(keys.DISCORD_TOKEN)
