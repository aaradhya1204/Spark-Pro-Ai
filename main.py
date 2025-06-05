import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
import PyPDF2
import os

# --- CONFIG ---
# WARNING: Exposing your API key directly in code is a serious security risk.
# This is for demonstration purposes ONLY and should NEVER be used in production
# or committed to public repositories.
# For production, always use st.secrets or environment variables.
API_KEY = "AIzaSyDuEXI97HF7gCU1lcwU5eHXZRf1Ma3ekBk" # REPLACE WITH YOUR ACTUAL API KEY
GEMINI_MODEL = "gemini-2.0-flash"

genai.configure(api_key=API_KEY)

# Initialize the generative model
model = genai.GenerativeModel(GEMINI_MODEL)

# --- STREAMLIT PAGE CONFIG ---
st.set_page_config(
    page_title="Spark 3.0 Pro AI Chatbot Made By Aaradhya Pratish Vanakhade",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.example.com/help',
        'Report a bug': 'https://www.example.com/bug',
        'About': '# This is a super cool AI chatbot powered by Google Gemini!'
    }
)

# --- CUSTOM CSS FOR STYLING ---
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');

    html, body, [class*="st-emotion"] {
        font-family: 'Poppins', sans-serif;
    }

    .header {
        background: linear-gradient(90deg, #6a11cb 0%, #20e2d7 100%); /* Vibrant gradient */
        padding: 20px 15px;
        border-radius: 12px;
        color: white;
        font-size: 32px;
        font-weight: 700;
        text-align: center;
        margin-bottom: 30px;
        box-shadow: 0 8px 15px rgba(0,0,0,0.2);
        letter-spacing: 1px;
    }

    .stApp {
        background-color: #f0f2f6; /* Light grey background */
    }

    .stFileUploader {
        border: 2px dashed #9b59b6; /* Purple dashed border */
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        margin-bottom: 25px;
        background-color: #fbfaff;
    }

    .stFileUploader label {
        font-size: 18px;
        font-weight: 600;
        color: #6a11cb;
    }

    .stButton > button {
        background-color: #20e2d7; /* Teal send button */
        color: #ffffff;
        border-radius: 8px;
        padding: 10px 25px;
        font-size: 18px;
        font-weight: 600;
        border: none;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        background-color: #1abc9c; /* Darker teal on hover */
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
        transform: translateY(-2px);
    }

    /* Chat message styling */
    .st-chat-message-container.st-chat-message-user .stChatMessage {
        background-color: #e0f7fa; /* Light cyan for user */
        border-radius: 15px 15px 0px 15px; /* Rounded corners */
        padding: 15px;
        margin-bottom: 15px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        color: #004d40;
        font-weight: 500;
    }
    .st-chat-message-container.st-chat-message-user .stChatMessage .avatar {
        background-color: #20e2d7; /* Teal avatar */
    }

    .st-chat-message-container.st-chat-message-assistant .stChatMessage {
        background-color: #ffffff; /* White for assistant */
        border-radius: 15px 15px 15px 0px; /* Rounded corners */
        padding: 15px;
        margin-bottom: 15px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        color: #333333;
        font-weight: 400;
        white-space: pre-wrap; /* Preserve line breaks */
    }
    .st-chat-message-container.st-chat-message-assistant .stChatMessage .avatar {
        background-color: #6a11cb; /* Purple avatar */
    }

    /* Input text area */
    .stTextArea label {
        font-size: 18px;
        font-weight: 600;
        color: #6a11cb;
    }
    .stTextArea textarea {
        border-radius: 10px;
        border: 1px solid #cccccc;
        padding: 10px;
        background-color: #ffffff;
    }
    .stTextArea textarea:focus {
        border-color: #6a11cb;
        box-shadow: 0 0 0 0.2rem rgba(106, 17, 203, 0.25);
    }

    /* Spinner animation */
    .stSpinner > div > div {
        color: #6a11cb !important;
    }

    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="header">😻 Spark 3.0 Pro AI Chatbot 🤖 Made By Aaradhya Pratish Vanakhade</div>', unsafe_allow_html=True)

# --- HELPER FUNCTIONS ---

def get_gemini_response(input_text, uploaded_file_content=None, file_type=None):
    """
    Gets a response from the Gemini model, handling multimodal inputs using gemini-2.0-flash.
    """
    try:
        parts = [input_text] # Start with the text prompt

        if uploaded_file_content and file_type:
            if file_type.startswith("image/"):
                img = Image.open(io.BytesIO(uploaded_file_content))
                parts.append(img)
            elif file_type == "application/pdf":
                pdf_reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file_content))
                text = ""
                for page_num in range(len(pdf_reader.pages)):
                    text += pdf_reader.pages[page_num].extract_text() + "\n"
                parts.append(f"\n\nContent from PDF:\n{text}")
            elif file_type.startswith("video/"):
                parts.append(f"\n\nYou mentioned a video. While I can process some video, for larger files or detailed analysis in this setup, please describe its content or ask specific questions about it.")
            # else: no specific handling for other file types, only text prompt will be sent

        response = model.generate_content(parts)

        return response.text
    except Exception as e:
        return f"Error: {e}. Could not get a response from the model. Please try again."

# --- CHAT HISTORY MANAGEMENT ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Initialize keys for input widgets if not already present
if "user_input_content" not in st.session_state:
    st.session_state.user_input_content = ""
if "file_uploader_key" not in st.session_state:
    st.session_state.file_uploader_key = 0 # This will be used to reset the uploader

# Display previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- FILE UPLOADER ---
uploaded_file = st.file_uploader(
    "🐾 **Upload an image, video, or PDF to chat about it!**",
    type=["png", "jpg", "jpeg", "mp4", "avi", "pdf"],
    accept_multiple_files=False,
    key=f"file_uploader_{st.session_state.file_uploader_key}" # Unique key for reset
)

uploaded_file_content = None
uploaded_file_type = None

if uploaded_file is not None:
    uploaded_file_content = uploaded_file.read()
    uploaded_file_type = uploaded_file.type
    st.info(f"✨ File '{uploaded_file.name}' ({uploaded_file_type}) uploaded. Now, ask me anything!")

# --- CHAT INPUT AND SEND BUTTON ---
# Set the default value of the text area from session_state.user_input_content
user_input = st.text_area(
    "💬 **What's on your mind?**",
    value=st.session_state.user_input_content, # Use value to control its content
    placeholder="Type your message here...",
    height=100,
    key="user_input_area" # Keep key for internal state management
)

col1, col2 = st.columns([1, 10])

with col1:
    send_button = st.button("Send", key="send_message_button")

# Handle sending message
if send_button and user_input.strip():
    # Append the user's current input to messages *before* clearing the input widget
    st.session_state.messages.append({"role": "user", "content": user_input.strip()})

    # Clear the input area content *in session state*
    st.session_state.user_input_content = ""
    # Increment the file uploader key to force it to reset
    st.session_state.file_uploader_key += 1

    # Get response from Gemini
    with st.chat_message("assistant"):
        with st.spinner("😼 Spark 3.0 Pro AI is thinking..."):
            # Pass the user_input that was just processed (before it got cleared from session_state)
            response = get_gemini_response(user_input.strip(), uploaded_file_content, uploaded_file_type)
            st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})

    st.experimental_rerun() # Rerun to reflect cleared input and new messages

# Optional: Add a clear chat button
if st.session_state.messages and st.sidebar.button("Clear Chat 🗑️"):
    st.session_state.messages = []
    st.session_state.user_input_content = "" # Clear text area content
    st.session_state.file_uploader_key += 1 # Reset file uploader
    st.experimental_rerun()