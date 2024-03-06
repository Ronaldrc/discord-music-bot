# Discord-Music-Bot

## Description
A discord bot capable of broadcasting audio from a YouTube video into a voice channel.

## Key Aspects
The user calls the slash command `/youtube` and writes a search phrase. This search phrase is sent to the YouTube API and returns the first video link it finds.
Audio from the video is extracted using youtube-dl and is converted using FFMPEG. This newly converted audio is played by the discord bot in the desired voice channel.

**Note: This project was created for educational purposes.**