import os
import requests
from gtts import gTTS
from moviepy.editor import *
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from tiktokapi import TikTokApi

# Acessando as variáveis de ambiente
TIKTOK_CLIENT_KEY = os.getenv('TIKTOK_CLIENT_KEY')
TIKTOK_CLIENT_SECRET = os.getenv('TIKTOK_CLIENT_SECRET')
YOUTUBE_CLIENT_ID = os.getenv('YOUTUBE_CLIENT_ID')
UNSPLASH_ACCESS_KEY = os.getenv('UNSPLASH_ACCESS_KEY')
UNSPLASH_SECRET_KEY = os.getenv('UNSPLASH_SECRET_KEY')

# Função para gerar narração do texto
def generate_narration(text):
    tts = gTTS(text=text, lang='pt')
    tts.save("narration.mp3")
    return "narration.mp3"

# Função para baixar uma imagem do Unsplash
def download_image():
    url = f"https://api.unsplash.com/photos/random?client_id={UNSPLASH_ACCESS_KEY}"
    response = requests.get(url)
    data = response.json()
    image_url = data[0]['urls']['regular']
    img_data = requests.get(image_url).content
    with open('image.jpg', 'wb') as handler:
        handler.write(img_data)

# Função para criar um vídeo
def create_video():
    # Baixar imagem do Unsplash
    download_image()

    # Adicionar a imagem como base para o vídeo
    image = ImageClip("image.jpg")
    image = image.set_duration(10)

    # Adicionar a narração
    narration = AudioFileClip("narration.mp3")
    video = image.set_audio(narration)

    # Salvar o vídeo
    video.write_videofile("final_video.mp4", fps=24)

# Função para upload no YouTube
def upload_to_youtube():
    SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secrets.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    youtube = build('youtube', 'v3', credentials=creds)
    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": "Video Automático",
                "description": "Descrição do vídeo automatizado"
            },
            "status": {
                "privacyStatus": "public"
            }
        },
        media_body=MediaFileUpload('final_video.mp4')
    )
    request.execute()

# Função para upload no TikTok
def upload_to_tiktok():
    api = TikTokApi.get_instance()
    video_path = "final_video.mp4"
    api.upload_video(video_path)

# Função principal
def main():
    text = "Olá, este é um vídeo automatizado criado com Python."
    generate_narration(text)
    create_video()
    upload_to_youtube()  # Descomente para upload no YouTube
    upload_to_tiktok()   # Descomente para upload no TikTok

if __name__ == "__main__":
    main()
