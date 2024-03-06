# Copyright Ron Chim 2024
# Date: 6 March 2024

import discord
import os
import youtube_dl
from dotenv import load_dotenv
from discord.ext import commands
from discord.ext.commands import bot
from discord import app_commands
from googleapiclient.discovery import build

intents = discord.Intents.default()
intents.guilds = True
intents.messages = True
intents.message_content = True

# For /youtube command - used in youtube player
# Notice: Volume set to 0.08 but is quite loud
FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5','options': '-vn -filter:a "volume=0.08"'}

# Define client, tree, and bot
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)
bot = commands.Bot(command_prefix='!', intents=intents)

# Get API key for ChatGPT from the .env file on my local machine
# Load .env file
load_dotenv()         # To access private keys and IDs in my .env file on my local machine

# Key for Google/Youtube API
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
DISCORD_BOT_KEY = os.getenv("DISCORD_BOT_KEY")

# My personal discord account ID
MY_DISCORD_ID = os.getenv("MY_DISCORD_ID")

# Perform on bot startup
# Sync all recently created slash commands 
@bot.event
async def on_ready():
    print('Youtube Music Bot is online! - POGGERS')
    try:
        synced = await bot.tree.sync()
        print(f"synched {len(synced)} command(s)")
    except Exception as e:
        print(e)

# Creates a youtube URL from the search phrase
# Play the youtube audio inside a voice channel
# Takes in an argument as a sentence
@bot.tree.command(name="youtube", description="Search and listen to youtube videos")
@app_commands.describe(prompt = "Type your search phrase here")
async def youtube(interaction: discord.Interaction, prompt: str):
    prompt = prompt + " audio"
    await interaction.response.defer()
    user_id = interaction.user.id
    guild = interaction.guild
    member = guild.get_member(user_id)

    # Continue if user is in a voice channel
    try:
        if member.voice == None:
            raise SyntaxError("member.voice is not valid")
    except:
        await interaction.followup.send(
            f"{interaction.user.mention} not in voice channel - please join a voice channel and try again", ephemeral=True
        )
        return

    # Get voice channel id of user
    voice_channel = member.voice.channel

    # FIXME: If not already in the same channel, bot joins the voice channel
    try:
        global voice_client
        voice_client = await voice_channel.connect()
    except:
        print("You are already connected to a voice channel - consider playing music")

    # Call Youtube API and build the URL with user's search phrase
    youtube = build('youtube', 'v3', developerKey=GOOGLE_API_KEY)
    request = youtube.search().list(
        part='snippet',
        q=prompt,
        type='video'
    )
    response = request.execute()
    videoID = response['items'][0]['id']['videoId']
    url = f"https://www.youtube.com/watch?v={videoID}"
    print(url)

    # Play audio in voice channel from url
    with youtube_dl.YoutubeDL({'format': 'bestaudio/best', 
                               'postprocessors': [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferredquality': '192',}]}) as ydl:
        # video_info is a dictionary full of info about the youtube video
        video_info = ydl.extract_info(url, download=False)
        audio_url = video_info.get("url", None)
        voice_client.play(discord.FFmpegPCMAudio(audio_url, **FFMPEG_OPTIONS))
        await interaction.followup.send(url)

@bot.tree.command(name="stop", description="call this command after youtube")
async def youtube(interaction: discord.Interaction):
    # try disconnect from the discord channel
    try:
        # voice_client is global variable
        await voice_client.disconnect()
    except Exception as e:
        print(f"Failed to disconnect bot from voice channel in /stop - {e}")
    interaction.response.send_message("Successfully stopped music! - Use /youtube to play another song", ephemeral=True)

bot.run(DISCORD_BOT_KEY)