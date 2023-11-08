import os
from googleapiclient.discovery import build
from dotenv import load_dotenv

class YoutubeLive():

    def __init__(self):
        load_dotenv()
        api_key = os.getenv("YOUTUBE_API_KEY")
        self.youtube = build('youtube', 'v3', developerKey=api_key)
        request = self.youtube.videos().list(
            part="liveStreamingDetails",
            id=os.getenv("YOUTUBE_VIDEO_ID")
        )
        response = request.execute()

        # Check if the live stream has an active chat
        if response['items'] and 'activeLiveChatId' in response['items'][0]['liveStreamingDetails']:
            self.live_chat_id = response['items'][0]['liveStreamingDetails']['activeLiveChatId']
        else:
            print("activeLiveChatId is invalid.")
            self.live_chat_id = None

        self.last_seen_message_ids = set()


    def get_live_chat_messages(self):
        if not self.live_chat_id:
            print("activeLiveChatId is invalid.")
            return []

        try:
            request = self.youtube.liveChatMessages().list(
                liveChatId=self.live_chat_id,
                part='id,snippet,authorDetails'
            )
            response = request.execute()
            return response.get('items', [])
        except Exception as e:
            print(f"An error occurred: {e}")
            return []

