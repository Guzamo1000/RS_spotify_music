from fastapi import APIRouter,HTTPException, Depends, status
from dotenv import load_dotenv
from fastapi.security import OAuth2PasswordBearer
import os
import httpx
import pandas as pd
from httpx import AsyncClient
from app.rs.utilis import model
from app.rs.utilis import extrac_future
load_dotenv()
data_song=pd.read_csv("/home/hau/Desktop/RS_spotify/API_RS_spotify/rs_sprotify_music/data/allsong_data.csv")
feature_song=pd.read_csv("/home/hau/Desktop/RS_spotify/API_RS_spotify/rs_sprotify_music/data/complete_feature.csv")
CLIENT_ID=os.getenv("CLIENT_ID")
CLIENT_SECRET=os.getenv("CLIENT_SECRET")
REDIRECT_URI="localhost:8000/token"
oauth2_schema=OAuth2PasswordBearer(tokenUrl="token")

router=APIRouter()
AUTH_URL = f"https://accounts.spotify.com/authorize?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code&scope=user-read-private%20user-read-email"

@router.get("/play/{track_id}")
async def play_track(track_id: str):
    if not CLIENT_ID or not CLIENT_SECRET:
        raise HTTPException(status_code=500, detail="missing spotify credentials")
    async with AsyncClient() as client:
        token_url="https://accounts.spotify.com/api/token"
        token_payload={
            "grant_type": "client_credentials",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
        }
        token_response=await client.post(token_url, data=token_payload)
        token_data=token_response.json()
        access_token=token_data['access_token']

        track_url = f"https://api.spotify.com/v1/tracks/{track_id}"
        headers = {"Authorization": f"Bearer {access_token}"}
        track_response = await client.get(track_url, headers=headers)
        track_data = track_response.json()
        # Extract the track's preview URL and return it
        preview_url = track_data.get("preview_url")
        if not preview_url:
            raise HTTPException(status_code=404, detail="Preview URL not available for the track")

        return {"preview_url": preview_url}

@router.get("/result")
async def home(url_track: str,number_of_rec:int):
    type_url=url_track.split("/")
    if type_url[3]=="track":
        df=extrac_future.extract_song(url_track)
    else:
        df=extrac_future.extract(url_track)
    music_recomment = model.recommend_from_playlist(data_song, feature_song, df)
    # print(f"edm: {edm_top40['track_pop']}")
    # number_of_recs = int(request.form['number-of-recs'])
    my_songs = []
    print(f"number record {number_of_rec}")
    if music_recomment is None: 
        # return render_template("results.html",songs=None)
        return {'status': "false", "mess":"song or playlist is not get feature"}
    print(f"music_recomment: {music_recomment}")
    for i in range(number_of_rec):
        
        my_songs.append([str(music_recomment.iloc[i,2]) + ' - '+ '"'+str(music_recomment.iloc[i,0])+'"', "https://open.spotify.com/track/"+ str(music_recomment.iloc[i,2]).split("/")[-1]])
    return {"song": my_songs}


