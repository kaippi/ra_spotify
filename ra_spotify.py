import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import sys
import requests
import base64
import urllib.request, json
import time
from selenium import webdriver
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
import pandas as pd

#Resident AdvisorのSingle Reviewのトラック情報を1ヶ月分取得
res = requests.get('https://www.residentadvisor.net/reviews.aspx?format=single&yr=2020&mn=2')
soup = BeautifulSoup(res.text, 'html.parser')
track = [i.get_text() for i in soup.select('h1')]

#取得したテキストをpd.Seriesに変換
track_list = pd.Series(track)

#0,1行目は不要なので除去
drop_idx = [0, 1]
track_list = track_list.drop(drop_idx)

#DataFrameを定義
df = pd.DataFrame(index=[], columns=['Track', 'Label'])

tracklist_len = len(track_list.index)

#トラック名＋アーティスト名、レーベル名を列としてDataFrameを作成
for i in range(0,tracklist_len,2):
    tmp = pd.Series([track_list.iloc[i],track_list.iloc[i+1]], index = df.columns)
    df =  df.append(tmp, ignore_index=True)

#トラック名とアーティスト名を分割して新規の列として追加し、既存の列を削除
#https://note.nkmk.me/python-pandas-split-extract/
df = pd.concat([df, df['Track'].str.split(' - ', expand=True)], axis=1).drop('Track', axis=1)

#列名を定義
df.columns = ['Label', 'Artist', 'Track']

#Noneを含む列を削除
df_dropped = df.dropna()
df_dropped = df_dropped.reset_index(drop=True)

#-------------------------------------------------------------------------------------

# ignored_exceptions=(StaleElementReferenceException,NoSuchElementException)

# def wdwfind(path):
#     return WebDriverWait(driver, 15,ignored_exceptions=ignored_exceptions).until(
#             EC.presence_of_element_located((By.XPATH,(path))))

#Parameters
playlist_id = "4CrXw4UfUEOg0yBJhWyAfW"
redirect_uri = "http://127.0.0.1:8080/"
trackID = []
spotifyUsername = "Spotifyのアカウント名"
spotifyPassword = "アカウントのパスワード"

driver = webdriver.Chrome()
driver.get('https://accounts.spotify.com/authorize?response_type=code&client_id=9c2c599cacf14ee29ab7e9e22aeea7e8&scope=playlist-modify-public&redirect_uri=http://127.0.0.1:8080/')
time.sleep(1)
driver.find_element_by_id('login-username').send_keys(spotifyUsername)
driver.find_element_by_id('login-password').send_keys(spotifyPassword)
driver.find_element_by_id('login-button').click()
time.sleep(1)
cur_url = urlparse(driver.current_url)
code = cur_url.query[5:]

def get_token_user(code, redirect_uri):
    url = "https://accounts.spotify.com/api/token"
    payload = {'grant_type':'authorization_code', 'code':code, 'redirect_uri':redirect_uri}
    headers = {'Authorization':'Basic OWMyYzU5OWNhY2YxNGVlMjlhYjdlOWUyMmFlZWE3ZTg6OWFkZWE5OWM1OTcyNDg0MDg0MTY2MTk0MzY1YWU2MDI='}
    response=requests.post(url, data=payload, headers=headers) 
    print(response.url)
    print(response.headers)
    data = response.json()
    return data['access_token']

def get_songUri(token):
    count = 0
    for i in range(len(df_dropped.index)):
        # https://developer.spotify.com/documentation/web-api/reference/search/search/#writing-a-query---guidelines
        url = 'https://api.spotify.com/v1/search'
        payload = {'q': df_dropped['Track'][i]+' artist:'+df_dropped['Artist'][i],'type':'track','limit':'1'}
        # payload = {'q':'idioteque artist:radiohead','type':'track','limit':'1'}
        headers = {'Authorization':'Bearer {}'.format(token)}
        response=requests.get(url, params=payload, headers = headers)
        response.raise_for_status()
        data =response.json()
        if data['tracks']['items'] != []:
            # items以下はlist形式なので[]で何番目の要素を取得するか指定する
            trackID.append(data["tracks"]["items"][0]["id"])
        else:
            count += 1
    print('There were '+ str(count) + ' tracks we could not found in Spotify')
        #return trackID

def add_playlist(token, playlist_id):
    count = 0
    for x in range(len(trackID)):
        # https://developer.spotify.com/documentation/web-api/reference/playlists/add-tracks-to-playlist/
        url = "https://api.spotify.com/v1/playlists/"+playlist_id+"/tracks"
        headers = {'Authorization':'Bearer '+token,'Content-Type':'application/json','Content-Length': '0','Accept':'application/json'}
        payload = {'uris':'spotify:track:'+trackID[x]}
        response=requests.post(url, params=payload, headers=headers)
        count += 1
    print(count + 'tracks were add in playlist!')

token = get_token_user(code,redirect_uri)
get_songUri(token)
add_playlist(token,playlist_id)