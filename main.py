from bs4 import BeautifulSoup
import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import configparser

config = configparser.ConfigParser()
config.read('config.ini')

CLIENT_ID = config.get('credentials', 'CLIENT_ID')
api_secret = config.get('credentials', 'api_secret')

# Navigates to billboard top 100 and scrapes the page for the top 100 songs on the date. Uses spotify API to create a playlist on my spotify with those songs.
# If song is not on list, it will skip over and print message.

OAUTH_AUTHORIZE_URL = "https://accounts.spotify.com/authorize"
OAUTH_TOKEN_URL = "https://accounts.spotify.com/api/token"
REDIRECT = "https://example.com/callback/"

# Logging into spotify

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=CLIENT_ID, client_secret=api_secret, scope="user-library-read playlist-modify-private", redirect_uri=REDIRECT,
    show_dialog=False, cache_path="token.txt"))

user_id = sp.current_user()["id"]

# Taking user input, scraping billboard for the songs of that year.
year = input("What date would you like to travel to? Please input like so- 'YYYY-MM-DD' (Include dashes)")

response = requests.get(f"https://www.billboard.com/charts/hot-100/{year}/")
billboard = response.text

soup = BeautifulSoup(billboard, "html.parser")

songs_table = soup.find("div", "chart-results-list")

songs = songs_table.find_all("h3", class_="a-no-trucate", id="title-of-a-story")
songs_list = [song.text.strip() for song in songs]
print(songs_list)

# Adding songs to the spotify playlist, if they aren't on spotify, skipping it.
song_uris = []
year = year.split("-")[0]
for song in songs_list:
    result = sp.search(q=f"track:{song} year:{year}", type="track")
    print(result)
    try:
        uri = result["tracks"]["items"][0]["uri"]
        song_uris.append(uri)
    except IndexError:
        print(f"{song} doesn't exist in Spotify. Skipped.")

playlist = sp.user_playlist_create(user=user_id, name=f"{year} Billboard 100", public=False)
# print(playlist)

sp.playlist_add_items(playlist_id=playlist["id"], items=song_uris)