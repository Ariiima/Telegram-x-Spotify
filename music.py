from telethon import TelegramClient, events
import asyncio
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from telethon.tl.types import PeerUser
import os
import configparser
import socks
import threading
import tracemalloc
tracemalloc.start()

global user_ids,sp,client,config
global user_ids,sp,client,config
config = configparser.ConfigParser()
config.read('config.ini')
os.environ['HTTP_PROXY'] = 'socks5://127.0.0.1:10808'
os.environ['HTTPS_PROXY'] = 'socks5://127.0.0.1:10808'
proxy = (socks.SOCKS5, '127.0.0.1',10808)

client_id = config['spotify']['client_id']
client_secret = config['spotify']['client_secret']
redirect_uri = config['spotify']['redirect_uri']
# initialize the Spotify client
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id,
                                            client_secret=client_secret,
                                            redirect_uri=redirect_uri,
                                            scope="user-read-playback-state,user-modify-playback-state,playlist-modify-private",
                                            cache_path="./home"))


# initialize the Telegram client

api_id = config['telegram']['api_id']
api_hash = config['telegram']['api_hash']
user_ids = [PeerUser(int(id)) for id in config['telegram']['user_ids'].split(',')]

print("Starting client...")
client = TelegramClient('my_account', int(api_id), api_hash,proxy=proxy)

def console_menu():
    print("Welcome to the Music Player!")
    print("1- Listen from User")
    print("2- Play a specific song")
    print("3- Add to queue")
    print("4- Play from playlist")
    choice = input("Enter your choice: ")
    return choice

async def play_song(song_name, sp):
    # Search for the song on Spotify
    results = sp.search(q=song_name, type='track', limit=1)
    if len(results['tracks']['items']) == 0:
        print("Song not found")
        return

    # Get the URI of the first search result
    uri = results['tracks']['items'][0]['uri']

    # Play the song on Spotify
    sp.start_playback(uris=[uri])
    await asyncio.sleep(1)
    current_track = sp.current_playback()
    if current_track is not None and current_track['is_playing']:
        song_name = current_track['item']['name']
        print(f"Now playing: {song_name}")

def standardize_phone_number(phone_number):
    if phone_number[0] == "+":
        return phone_number
    elif phone_number[0] == "0":
        return "+98" + phone_number[1:]
    else:
        return "+98" + phone_number

async def listen_from_user():
    global user_ids,sp,client,config
    print("Do you want to add user from Username or Phone Number?")
    print("1- Username")
    print("2- Phone Number")
    choice = input("Enter your choice: ")
    if choice == "1":
        username = input("Enter the username: ")
        # get id from username and add to user_ids
        entity = await client.get_entity(username)
        # get id from username
        user_id = entity.id
        user_ids.append(PeerUser(int(user_id)))
    elif choice == "2":
        phone_number = input("Enter the phone number: ")
        phone_number = standardize_phone_number(phone_number)
        # get id from phone number and add to user_ids
        entity = await client.get_entity(phone_number)
        # get id from phone number
        user_id = entity.id
        user_ids.append(PeerUser(int(user_id)))


def add_to_queue():
    # Do something
    pass


def play_from_playlist():
    # Do something
    pass


async def menu():
    global user_ids,sp,client,config
    while True:
        choice = console_menu()
        if choice == "1":
            # await listen_from_user()
            print("Still not implemented fully")
        elif choice == "2":
            # Play a specific song
            song_name = input("Enter the song name: ")
            await play_song(song_name, sp)
        elif choice == "3":
            add_to_queue()
        elif choice == "4":
            play_from_playlist()
        else:
            print("Invalid choice")


# Start the menu thread
menu_thread = threading.Thread(target=menu)
menu_thread.start()

async def incoming_message_handler(event):
    global user_ids,sp,client,config
    print(event.message.message)
    global flag
    if event.message.from_id in user_ids:
        # check for the '!music:' command
        if event.message.message.startswith("!music"):
            music_name = event.message.message[7:]
            # search for the song on Spotify
            results = sp.search(q=music_name, limit=1, type='track')
            if results and results['tracks'] and results['tracks']['items']:

                # start playing the song
                await play_song(music_name, sp)

                # Send the song link to the bot
                track_uri = results['tracks']['items'][0]['uri']
                song_link = results['tracks']['items'][0]['external_urls']['spotify']
                await client.send_message('motreb_downloader_bot', song_link)

                # wait for motreb to send the song
                await asyncio.sleep(5)

                # Get the last message from the bot
                last_message = await client.get_messages('motreb_downloader_bot', limit=2)
                # print(last_message[1].message)
                # await client.edit_message(last_message[1], "", entities=None)
                # Forward the message to the user
                await client.forward_messages(user_ids[0], last_message[1])

                # add to playlist
                playlist_id = config['spotify']['playlist_id']
                sp.playlist_add_items(playlist_id, [track_uri])


@client.on(events.NewMessage(incoming=True))
async def start(event):
    await main()

async def main():
    global user_ids,sp,client,config
    await menu()

    async def check_song_end():
        last_track = None
        while True:
            current_track = sp.current_playback()
            # print(current_track)
            if current_track is not None:
                if last_track is not None and last_track['item']['uri'] != current_track['item']['uri']:
                    # Song has changed, so the last one must have ended
                    message = "Song ended"
                    await client.send_message(user_ids[0], message)
                        
                last_track = current_track
            await asyncio.sleep(5)  # Wait for 5 seconds before checking again

    asyncio.create_task(check_song_end())
    client.start()
    client.run_until_disconnected()

asyncio.run(main())


