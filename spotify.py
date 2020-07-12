import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import sys
import requests
import base64
import urllib.request, json
import time
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait as Wait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import ActionChains
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
import pandas as pd

res = requests.get('https://www.residentadvisor.net/reviews.aspx?format=single&yr=2020&mn=4')
soup = BeautifulSoup(res.text, 'html.parser')
text = [i.get_text() for i in soup.select('h1')]

text = pd.Series(text)
#print(text)
pd.set_option('display.max_rows', 50)

#drop_idx = [0,1]
text_droped = text.drop(text.index[:10])
#print(text_droped)

text_split = text_droped.str.split('-')
#print(text_split)

album = pd.Series()
cols = ['col1', 'col2']
df = pd.DataFrame(index=[], columns=list('AB'))

text_length = len(text_droped.index)
#print(text_length)
text_half = text_length//2 -1
#print(text_half)

count = 0

for i in range(0,text_length,2):
    tmp = pd.Series([text_droped.iloc[i],text_droped.iloc[i+1]], index = df.columns)
    df =  df.append(tmp, ignore_index=True)
    text_half = len(text_droped.index)
    count += 1

tmp = df['A'].str.split('-', expand=True)
#tmp = tmp[0].str.split(' - ', expand=True)
df['Artist'] = tmp[0]
df['Song'] = tmp[1]

ignored_exceptions=(StaleElementReferenceException,NoSuchElementException)

def wdwfind(path):
    return WebDriverWait(driver, 15,ignored_exceptions=ignored_exceptions).until(
            EC.presence_of_element_located((By.XPATH,(path))))

driver = webdriver.Chrome()
driver.get('https://accounts.spotify.com/authorize?response_type=code&client_id=9c2c599cacf14ee29ab7e9e22aeea7e8&scope=playlist-modify-public&redirect_uri=http://127.0.0.1:8080/')
time.sleep(1)
driver.find_element_by_id('login-username').send_keys("ochokocho@gmail.com")
driver.find_element_by_id('login-password').send_keys("fizzfuzz")
driver.find_element_by_id('login-button').click()
time.sleep(1)
cur_url = urlparse(driver.current_url)
code = cur_url.query[5:]

client_id = '9c2c599cacf14ee29ab7e9e22aeea7e8'
client_secret = '9adea99c5972484084166194365ae602'
client_credentials_manager = spotipy.oauth2.SpotifyClientCredentials(client_id, client_secret)
spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

base64_client_id = str(base64.b64encode(client_id.encode('utf-8')))
base64_client_secret = str(base64.b64encode(client_secret.encode('utf-8')))
encoded_data = base64.b64encode(bytes(f"{client_id}:{client_secret}", "ISO-8859-1")).decode("ascii")
redirect_uri = "http://127.0.0.1:8080/"
# def get_code():
#     url = "https://accounts.spotify.com/authorize?response_type=code&client_id=9c2c599cacf14ee29ab7e9e22aeea7e8&scope=playlist-modify-public&redirect_uri=http://127.0.0.1:8080/"
#     response=requests.get(url)
#     return response.text

def get_token():
    url = "https://accounts.spotify.com/api/token"
    payload = {'grant_type':'client_credentials'}
    headers = {'Authorization':'Basic OWMyYzU5OWNhY2YxNGVlMjlhYjdlOWUyMmFlZWE3ZTg6OWFkZWE5OWM1OTcyNDg0MDg0MTY2MTk0MzY1YWU2MDI='}
    response=requests.post(url, data=payload, auth = (client_id, client_secret)) 
    data = response.json()
    return data['access_token']

def get_token_user(code, redirect_uri):
    url = "https://accounts.spotify.com/api/token"
    payload = {'grant_type':'authorization_code', 'code':code, 'redirect_uri':redirect_uri}
    headers = {'Authorization':'Basic OWMyYzU5OWNhY2YxNGVlMjlhYjdlOWUyMmFlZWE3ZTg6OWFkZWE5OWM1OTcyNDg0MDg0MTY2MTk0MzY1YWU2MDI='}
    response=requests.post(url, data=payload, headers=headers) 
    print(response.url)
    print(response.headers)
    data = response.json()
    return data['access_token']

def get_songUri(token,track):
    trackID = []
    for i in range(len(df.index)):
        # https://developer.spotify.com/documentation/web-api/reference/search/search/#writing-a-query---guidelines
        url = 'https://api.spotify.com/v1/search'
        payload = {'q': df['Song'][0]+' artist:'+df['Artist'][0],'type':'track','limit':'1'}
        # payload = {'q':'idioteque artist:radiohead','type':'track','limit':'1'}
        headers = {'Authorization':'Bearer {}'.format(token)}
        response=requests.get(url, params=payload, headers = headers)
        data =response.json()
        print(response.url)
        trackID.append(data["tracks"]["items"][0]["id"])
        # return "{}".format(json.dumps(data,indent=4))
        # items以下はlist形式なので[]で何番目の要素を取得するか指定する
    return trackID

def add_playlist(token, playlist_id, track_id):
    for i in range(len(track_id)):
        # https://developer.spotify.com/documentation/web-api/reference/playlists/add-tracks-to-playlist/
        url = "https://api.spotify.com/v1/playlists/"+playlist_id+"/tracks"
        headers = {'Authorization':'Bearer '+token,'Content-Type':'application/json','Content-Length': '0','Accept':'application/json'}
        payload = {'uris':'spotify:track:'+track_id[i]}
        response=requests.post(url, params=payload, headers=headers)
    return response

track = [
    {'track':'closer',
    'artists':'nine inch nails'
    },
    {'track':'idioteque',
    'artists':'radiohead'
    }
]

# token = 'BQC70exxXDdXcwuNpNfLtFulpg2mcbcfiYolgK7wJ9SxdmUIT7nAEu-FElrdU4Ru78s70SVlMchgb4hHOSFsDOr7acH2EAFtZRP1kRIbF6piJeZTKEUTfeiurz0NdROxjiwHQE7gSzfmSqi1tQad0IvBemAdnopSIfW-fZppQNdtlEP76Uo'

token = get_token_user(code, redirect_uri)

track_id = get_songUri(token,track)
playlist_id = "4CrXw4UfUEOg0yBJhWyAfW"
r = add_playlist(token,playlist_id,track_id)
print(r)

# curl -X "POST" "https://api.spotify.com/v1/playlists/4CrXw4UfUEOg0yBJhWyAfW/tracks?uris=spotify%3Atrack%3A57ZXcBtCZXSg9TVV5xRdnR" -H "Accept: application/json" -H "Content-Type: application/json" -H "Content-Length: 0" -H "Authorization: Bearer BQAT4IQ7Gh2Mv5QqPMc5UDDXgKkGYypjOvZMIrrvb8nT7m-U3__A_S1FBHN30nuBGHzdcTYXOM0tGscok0k"
# curl -X GET "https://api.spotify.com/v1/search?q=tania%20bowra&type=artist" -H "Authorization: Bearer BQDgJH7WUIplQC5N4EdOq-Nb_ZHovrNoxEm3MkN8En1GpGYkcO0jQR2XlmuhE7tzGG56mNHZe0fmV_QR070"
# curl -X "POST" -H "Authorization: Basic OWMyYzU5OWNhY2YxNGVlMjlhYjdlOWUyMmFlZWE3ZTg6OWFkZWE5OWM1OTcyNDg0MDg0MTY2MTk0MzY1YWU2MDI=" -d grant_type=client_credentials https://accounts.spotify.com/api/token

# results = spotify.artist_top_tracks(lz_uri)

# for track in results['tracks'][:10]:
#     print('track    : ' + track['name'])
#     print('audio    : ' + track['preview_url'])
#     print('cover art: ' + track['album']['images'][0]['url'])
#     print()