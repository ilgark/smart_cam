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

# State für Kameraauswahl
if 'use_front_camera' not in st.session_state:
    st.session_state['use_front_camera'] = True

def switch_camera():
    st.session_state['use_front_camera'] = not st.session_state['use_front_camera']

# Button zum Wechseln der Kamera
camera_button_label = "Switch to Rear Camera" if st.session_state['use_front_camera'] else "Switch to Front Camera"
st.button(camera_button_label, on_click=switch_camera)

# Kamera-Einstellung
camera_facing_mode = "user" if st.session_state['use_front_camera'] else "environment"

# WebRTC-Streamer einrichten
webrtc_streamer(
    key="example",
    mode=WebRtcMode.SENDRECV,
    video_frame_callback=replace_background,
    media_stream_constraints={
        "video": {
            "facingMode": {"exact": camera_facing_mode}
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
