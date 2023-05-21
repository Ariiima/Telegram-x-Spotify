from telethon import TelegramClient, events
import asyncio
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from telethon.tl.types import PeerUser
import os
import configparser


async def main():
    config = configparser.ConfigParser()
    config.read('config.ini')
    os.environ['HTTP_PROXY'] = 'socks5://127.0.0.1:10808'
    os.environ['HTTPS_PROXY'] = 'socks5://127.0.0.1:10808'

    client_id = config['spotify']['client_id']
    client_secret = config['spotify']['client_secret']
    redirect_uri = config['spotify']['redirect_uri']

    # initialize the Spotify client
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id,
                                                client_secret=client_secret,
                                                redirect_uri=redirect_uri,
                                                scope="user-read-playback-state,user-modify-playback-state",
                                                cache_path="./home"))


    # initialize the Telegram client

    api_id = config['telegram']['api_id']
    api_hash = config['telegram']['api_hash']
    user_ids = [PeerUser(int(id)) for id in config['telegram']['user_ids'].split(',')]

    print("Starting client...")
    client = TelegramClient('my_account', int(api_id), api_hash)
        
    flag =0
    @client.on(events.NewMessage(incoming=True))
    async def incoming_message_handler(event):
        global flag
        if event.message.from_id in user_ids:
            # check for the '!music:' command
            if event.message.message.startswith("!music:"):
                music_name = event.message.message[7:]
                # search for the song on Spotify
                results = sp.search(q=music_name, limit=1, type='track')
                if results['tracks']['items']:
                    flag =1
                    track_uri = results['tracks']['items'][0]['uri']
                    track_name = results['tracks']['items'][0]['name']
                    track_artist = results['tracks']['items'][0]['artists'][0]['name']
                    # start playing the song
                    sp.start_playback(uris=[track_uri])
                    # Send the song link to the bot
                    song_link = results['tracks']['items'][0]['external_urls']['spotify']
                    await client.send_message('motreb_downloader_bot', song_link)
                    await asyncio.sleep(7)

                    # Get the last message from the bot
                    last_message = await client.get_messages('motreb_downloader_bot', limit=2)
                    print(last_message[1].message)
                    # await client.edit_message(last_message[1], "", entities=None)
                    # Forward the message to the user
                    await client.forward_messages(user_ids[1], last_message[1])

                    # Check if the song is still playing
                    current_track = sp.current_playback()
                    if current_track is not None and current_track['is_playing']:
                        # Song is still playing
                        message = f"Song '{track_name}' by {track_artist} played"
                        await client.send_message(user_ids[1], message)
                    
    async def check_song_end():
        last_track = None
        while True:
            current_track = sp.current_playback()
            print(current_track)
            if current_track is not None:
                if last_track is not None and last_track['item']['uri'] != current_track['item']['uri']:
                    # Song has changed, so the last one must have ended
                    message = "Song ended"
                    await client.send_message(user_ids[1], message)
                    flag = 0
                last_track = current_track
            await asyncio.sleep(5)  # Wait for 5 seconds before checking again

    asyncio.create_task(check_song_end())
    await client.start()
    await client.run_until_disconnected()

asyncio.run(main())

