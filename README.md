# Discord-Music-Bot

## Description
A discord bot capable of broadcasting audio from a YouTube video into a voice channel.

## Detailed Scription
1. The user calls the slash command `/youtube` and writes a search phrase.
2. This search phrase is sent to the YouTube API and returns the first video link it finds.
3. Audio from the video is extracted using youtube-dl and is converted using FFMPEG.
4. This newly converted audio is played by the discord bot in the desired voice channel.

## Key Aspects
- Calls to Discord API
- Calls to YouTube API
- Learn about youtube-dl and use library
- Learn about audio processing and streaming
- Learn about asynchronous programming

## Note
**This project was created for educational purposes.**