import streamlit as st
import cv2
from cvzone.SelfiSegmentationModule import SelfiSegmentation
import numpy as np
import time

# Streamlit Interface
st.title("Kamera mit Hintergrundwechsel")

# Auswahl der Kamera
camera_option = st.selectbox("Wählen Sie die Kamera", ("Vorderkamera", "Rückkamera"))
camera_index = 0 if camera_option == "Vorderkamera" else 1

# Datei-Upload für Hintergrundbild
uploaded_file = st.file_uploader("Laden Sie ein Hintergrundbild hoch", type=["jpg", "jpeg", "png"])

# Kamera starten
camera = cv2.VideoCapture(camera_index)
if not camera.isOpened():
    st.error("Kamera konnte nicht geöffnet werden.")
else:
    segmentor = SelfiSegmentation()
    frame_window = st.empty()
    background_img = None

    # Zustand zum Beenden der Schleife
    stop = st.button('Beenden', key='stop_button')

    # Hauptschleife für die Anzeige des Video-Feeds
    while not stop:
        success, img = camera.read()
        if not success or img is None:
            st.error("Bild konnte nicht von der Kamera gelesen werden.")
            break

        # Webcam-Bild auf 640x480 skalieren
        try:
            img = cv2.resize(img, (640, 480))
        except cv2.error as e:
            st.error(f"Fehler beim Skalieren des Bildes: {e}")
            break

        # Wenn ein Hintergrundbild hochgeladen wurde, ersetze den Hintergrund
        if uploaded_file is not None:
            if background_img is None:
                file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
                background_img = cv2.imdecode(file_bytes, 1)
                background_img = cv2.resize(background_img, (640, 480))
            img = segmentor.removeBG(img, background_img, threshold=0.8)

        # Video anzeigen
        frame_window.image(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))

        # Kleine Pause für einen reibungslosen Video-Feed
        time.sleep(0.01)

        # Überprüfen, ob der Benutzer die Schaltfläche "Beenden" geklickt hat
        stop = st.button('Beenden', key='stop_button')

    camera.release()
    cv2.destroyAllWindows()
