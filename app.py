import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase, WebRtcMode
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
    key="camera",
    mode=WebRtcMode.SENDRECV,
    video_processor_factory=VideoTransformer,
    media_stream_constraints={
        "video": {
            "facingMode": {"exact": st.session_state.camera_type}
        }
    }
)
