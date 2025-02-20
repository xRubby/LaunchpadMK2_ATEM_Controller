#youtube_api.py

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os
import pickle

SCOPES = ["https://www.googleapis.com/auth/youtube.readonly"]

credentials_file = 'credentials.json'

def get_authenticated_service() -> any:
    creds = None

    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token_file:
            creds = pickle.load(token_file)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)

        with open("token.pickle", "wb") as token_file:
            pickle.dump(creds, token_file)

    youtube = build("youtube", "v3", credentials=creds)
    return youtube

def get_live_broadcasts(youtube) -> any:
    request = youtube.liveBroadcasts().list(
        part="snippet,contentDetails,status",
        broadcastStatus="active",
        broadcastType="all"
    )
    response = request.execute()
    return response

async def isLive() -> bool:
    if os.path.exists(credentials_file):
        youtube = get_authenticated_service()
        live_broadcasts = get_live_broadcasts(youtube)
        if live_broadcasts:

            try:
                live = live_broadcasts["items"][0]["snippet"]["title"]
                return True
            except Exception as e:
                return False
        return False

if __name__ == "__main__":
   
    if isLive():
        print (f"Il canale è in live")
    else:
        print (f"Il canale non è in live")