import cv2
import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoHTMLAttributes, WebRtcMode
import numpy as np
import av
from cvzone.SelfiSegmentationModule import SelfiSegmentation

st.set_page_config(layout="wide")

st.title("Background Replacement with OpenCV and SelfiSegmentation")

# Initialer Zustand des Hintergrunds
if 'background_img' not in st.session_state:
    st.session_state['background_img'] = np.zeros((480, 640, 3), dtype=np.uint8)

# Funktion zur Hintergrundersetzung
def replace_background(frame: av.VideoFrame) -> av.VideoFrame:
    img = frame.to_ndarray(format="bgr24")
    
    # Hintergrund entfernen und mit Hintergrundbild kombinieren
    segmentor = SelfiSegmentation()
    img_out = segmentor.removeBG(img, st.session_state['background_img'], threshold=0.8)
    
    return av.VideoFrame.from_ndarray(img_out, format="bgr24")

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
        style={"width": "100%", "height": "90vh", "object-fit": "cover", "z-index": "1"}  # Setzt das Video auf 90% der Bildschirmhöhe
    )
)
