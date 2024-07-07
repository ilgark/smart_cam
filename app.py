import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase, WebRtcMode, VideoHTMLAttributes
import av

st.title("Streamlit Kamera App")

# Speicherung des aktuellen Kamera-Typs im Session State
if "camera_type" not in st.session_state:
    st.session_state.camera_type = "user"  # Standardmäßig vordere Kamera

# Funktion zum Umschalten der Kamera
def switch_camera():
    if st.session_state.camera_type == "user":
        st.session_state.camera_type = "environment"
    else:
        st.session_state.camera_type = "user"

# Knopf zum Umschalten der Kamera
st.button("Wechsel Kamera", on_click=switch_camera)

# Transformator Klasse zur Verarbeitung der Videodaten
class VideoTransformer(VideoTransformerBase):
    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")
        return av.VideoFrame.from_ndarray(img, format="bgr24")

# WebRTC Streamer
webrtc_streamer(
    key="example",
    mode=WebRtcMode.SENDRECV,
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
        style={"width": "100%", "height": "calc(100vh - 120px)", "object-fit": "cover", "transform": "rotate(90deg)", "z-index": "1"}  # Vertikale Ausrichtung
    )
)