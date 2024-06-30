# Copyright Ron Chim 2024
# Date: 20 June 2024

# Next steps:
# Make asynchronous queue to add songs to beginning of list or end of list - add next AND add last
# Allow users to skip songs
# Allows users to view songs in queue - view entire list of songs

import discord
import os
import asyncio
import yt_dlp as youtube_dl
from dotenv import load_dotenv
from discord.ext import commands
from discord import app_commands
from googleapiclient.discovery import build

intents = discord.Intents(messages=True, guilds=True, members=True, message_content=True)

# For /youtube command - used in youtube player
# Notice: Volume set to 0.05 but is quite loud
FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5','options': '-vn -filter:a "volume=0.05"'}

# Define client, tree, and bot
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)
bot = commands.Bot(command_prefix='!', intents=intents)

# Get API key for ChatGPT from the .env file on my local machine
# Load .env file
load_dotenv()         # To access private keys and IDs in my .env file on my local machine

# Key for Google/Discord API
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
DISCORD_BOT_KEY = os.getenv("DISCORD_BOT_KEY")

# Perform on bot startup
# Sync all recently created slash commands 
@bot.event
async def on_ready():
    print('Youtube Music Bot is online! - use /youtube to play music')
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
    prompt = prompt + " audio"      # Audio videos contain only music
    await interaction.response.defer()
    user_id = interaction.user.id
    guild = interaction.guild
    member = guild.get_member(user_id)
    member_voice_state = member.voice

    # Continue if user is in a voice channel
    if member_voice_state is None:
        return await interaction.followup.send(f"{interaction.user.mention} not in voice channel - please join a voice channel and try again", ephemeral=True)

    # Get voice channel id of user
    voice_channel = member.voice.channel

    # FIXME: So, if not already in the same channel, bot joins the voice channel
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
    
    # Save dictionary as json so i can learn to extract needed info
    # with open('data.json', 'w') as fp:
    #     json.dump(response, fp)

    videoID = response['items'][0]['id']['videoId']
    url = f"https://www.youtube.com/watch?v={videoID}"
    print(url)

    # Play audio in voice channel from url
    with youtube_dl.YoutubeDL({'format': 'bestaudio/best', 
                               'postprocessors': [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferredquality': '192',}]}) as ydl:
        # video_info is a dictionary full of info about the youtube video
        video_info = ydl.extract_info(url, download=False)
        audio_url = video_info.get("url", None)

        try:
            voice_client.play(discord.FFmpegPCMAudio(audio_url, **FFMPEG_OPTIONS))
        except discord.errors.ClientException as e:
            interaction.followup.send("Failed to play voice client")
            return None
        except Exception as e:
            print(f"Failed to connect to voice client - {e}")
            interaction.followup.send("Failed to play voice client")
            return None

        # Create embedded message and send in discord
        title = response['items'][0]['snippet']['title']
        thumbnail_url = response['items'][0]['snippet']['thumbnails']['default']['url']
        embeded_var = discord.Embed(title=f"Now Playing...\n\n{title}\n\nRequester", description=f"{interaction.user.mention}", colour=0x992d22)
        embeded_var.set_thumbnail(url=thumbnail_url)
        await interaction.followup.send(embed=embeded_var)

@bot.tree.command(name="stop", description="call this command after youtube")
async def youtube(interaction: discord.Interaction):
    global voice_client
    # try disconnect from the discord channel
    if voice_client:
        try:
            await voice_client.disconnect()
        except Exception as e:
            print(f"Failed to disconnect bot from voice channel in /stop - {e}")
        await interaction.response.send_message("Successfully stopped music! - Use /youtube to play another song", ephemeral=True)
    else:
        await interaction.response.send_message("Already disonnected - Use /youtube to play another song", ephemeral=True)

bot.run(DISCORD_BOT_KEY)
