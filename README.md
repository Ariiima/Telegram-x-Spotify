# Music.py

Music.py is a Python script that listens to a Telegram chat for commands and plays the requested song on Spotify.

## Prerequisites

Before you can use Music.py, you need to have the following:

- A Spotify account
- A Telegram account
- Python 3.6 or later
- The following Python packages:
  - `spotipy`
  - `telethon`

## Installation

To install Music.py, follow these steps:

1. Clone the repository to your local machine:
```
git clone https://github.com/Ariiima/music.py.git
```  

2. Install the required Python packages:
```
pip install -r requirements.txt
```

3. Create a `config.ini` file in the root directory of the project with the following contents:
```
[SPOTIFY]
CLIENT_ID=<your-spotify-client-id>
CLIENT_SECRET=<your-spotify-client-secret>
REDIRECT_URI=<your-spotify-redirect-uri>

[TELEGRAM]
API_ID=<your-telegram-api-id>
API_HASH=<your-telegram-api-hash>
USER_IDS=<comma-separated-list-of-telegram-user-ids>
```

Replace the values in angle brackets with your own values.

4. Run the script:

`python music.py`


## Usage

To use Music.py, follow these steps:

1. Start the script by running the `music.py` file.

2. When users (defined in config.ini) use the command !music: [songn name]
in your chat, code connects to spotify api and plays that song.

I will write about specifics of getting the API keys and setting up the bot in the future.
