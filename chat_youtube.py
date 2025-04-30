import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
from openai import OpenAI
import tempfile
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Streamlit
st.set_page_config(
    page_title="Chat with YouTube Video",
    page_icon="📺",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Streamlit server configuration
os.environ['STREAMLIT_SERVER_PORT'] = '8080'
os.environ['STREAMLIT_SERVER_ADDRESS'] = '0.0.0.0'
os.environ['STREAMLIT_SERVER_BASEURL'] = '/youtube-chat'
os.environ['STREAMLIT_SERVER_ENABLE_CORS'] = 'true'

def extract_video_id(video_url: str) -> str:
    if "youtube.com/watch?v=" in video_url:
        return video_url.split("v=")[-1].split("&")[0]
    elif "youtube.com/shorts/" in video_url:
        return video_url.split("/shorts/")[-1].split("?")[0]
    else:
        raise ValueError("Invalid YouTube URL")

def fetch_video_transcript(video_url: str) -> str:
    try:
        video_id = extract_video_id(video_url)
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join([entry["text"] for entry in transcript])
    except Exception as e:
        st.error(f"Error fetching transcript: {e}")
        return None

# Create Streamlit app
st.title("Chat with YouTube Video 📺")
st.caption("This app allows you to chat with a YouTube video using OpenAI API")

# Get OpenAI API key from environment variable
openai_api_key = os.getenv("OPENAI_API_KEY")

if not openai_api_key:
    st.error("OpenAI API key not found in .env file. Please add your API key to the .env file.")
    st.stop()

client = OpenAI(api_key=openai_api_key)

# Get the YouTube video URL from the user
video_url = st.text_input("Enter YouTube Video URL")

if video_url:
    transcript = fetch_video_transcript(video_url)
    if transcript:
        st.success("Transcript loaded successfully!")
        
        # Ask a question about the video
        question = st.text_input("Ask any question about the video")
        
        if question:
            try:
                # Create a prompt that includes the transcript and question
                prompt = f"""Based on the following YouTube video transcript, please answer the question. 
                If the answer cannot be found in the transcript, say "I cannot find the answer in the video transcript."

                Transcript:
                {transcript}

                Question: {question}
                """
                
                # Get response from OpenAI
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant that answers questions about YouTube video content."},
                        {"role": "user", "content": prompt}
                    ]
                )
                
                # Display the answer
                st.write("Answer:", response.choices[0].message.content)
                
            except Exception as e:
                st.error(f"Error getting response: {e}")
    else:
        st.error("Could not fetch the video transcript. Please check if the video has captions enabled.")