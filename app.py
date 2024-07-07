import cv2
import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoHTMLAttributes, WebRtcMode
import numpy as np
import av

st.set_page_config(layout="wide")

st.title("Background Replacement with OpenCV")

# Initialer Zustand des Hintergrunds
if 'background_img' not in st.session_state:
    st.session_state['background_img'] = np.zeros((480, 640, 3), dtype=np.uint8)

# Funktion zur Hintergrundersetzung
def replace_background(frame: av.VideoFrame) -> av.VideoFrame:
    img = frame.to_ndarray(format="bgr24")

    # Hintergrundsubtraktion (Beispiel: einfache Farbschwelle)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, np.array([35, 100, 100]), np.array([85, 255, 255]))  # Beispiel für grüne Farbe
    mask_inv = cv2.bitwise_not(mask)
    
    fg = cv2.bitwise_and(img, img, mask=mask_inv)
    bg = cv2.bitwise_and(st.session_state['background_img'], st.session_state['background_img'], mask=mask)
    
    combined = cv2.add(fg, bg)

    return av.VideoFrame.from_ndarray(combined, format="bgr24")

# Funktion zum Hochladen und Einstellen des neuen Hintergrundbildes
uploaded_file = st.file_uploader("Upload a background image", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    image = cv2.imdecode(file_bytes, 1)
    st.session_state['background_img'] = cv2.resize(image, (640, 480))

# WebRTC-Streamer einrichten
webrtc_streamer(
    key="example",
    mode=WebRtcMode.SENDRECV,
    video_frame_callback=replace_background,
    media_stream_constraints={
        "video": {
            "facingMode": {"exact": "user"}  # Frontkamera auswählen
        },
        "audio": False
    },
    rtc_configuration={
        "iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]
    },
    video_html_attrs=VideoHTMLAttributes(
        autoPlay=True,
        controls=False,
        style={"width": "100%", "height": "80vh", "object-fit": "cover", "z-index": "1"}  # Setzt das Video auf 80% der Bildschirmhöhe
    )
)

# Platz für zusätzlichen Streamlit-Inhalt oben und unten
st.write("Additional Streamlit content can go here...")

# Knopf zum Ändern des Hintergrunds in der Mitte unten
st.markdown(
    """
    <style>
    .button-container {
        position: fixed;
        bottom: 20px;
        width: 100%;
        text-align: center;
        z-index: 9999;
    }
    .button-container button {
        font-size: 20px;
        padding: 10px 20px;
        background-color: #4CAF50;
        color: white;
        border: none;
        border-radius: 5px;
        cursor: pointer;
    }
    .button-container button:hover {
        background-color: #45a049;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="button-container"><button onclick="window.streamlitChangeBackground()">Change Background</button></div>', unsafe_allow_html=True)

if st.button("Change Background"):
    if uploaded_file is not None:
        st.session_state['background_img'] = cv2.resize(image, (640, 480))
    else:
        st.warning("Please upload a background image first.")