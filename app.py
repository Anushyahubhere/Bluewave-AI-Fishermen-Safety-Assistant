
    # BlueWave AI - Fishermen Safety Assistant (Full Features)
import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import datetime
import pydeck as pdk
import pandas as pd
import requests
from google.protobuf.json_format import MessageToDict
from streamlit_lottie import st_lottie
from gtts import gTTS
import base64
import os
import random
import time

# Initialize Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate(dict(st.secrets["firebase"]))
    firebase_admin.initialize_app(cred)
db = firestore.client()

# Load Lottie animation
def load_lottie_url(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# Voice alert generator
def speak(text, lang='en'):
    tts = gTTS(text, lang=lang)
    tts.save("alert.mp3")
    audio_file = open("alert.mp3", "rb")
    audio_bytes = audio_file.read()
    st.audio(audio_bytes, format='audio/mp3')

# Layout setup
st.set_page_config(page_title="BlueWave AI - Fishermen Safety Assistant", layout="wide")
st.title("BlueWave AI - Fishermen Safety Assistant")

# Multilingual toggle
lang = st.sidebar.selectbox("Language / மொழி", ["English", "தமிழ்"])
translate = {"English": lambda x: x, "தமிழ்": lambda x: f"(தமிழில்) {x}"}  # Dummy switcher

# Real-time location tracking
st.header(translate[lang]("1. Real-Time GPS Tracking"))
latitude = st.number_input("Latitude", value=8.0883, format="%.6f")
longitude = st.number_input("Longitude", value=77.5385, format="%.6f")
st.map(pd.DataFrame([[latitude, longitude]], columns=['lat', 'lon']))

# SOS alert
st.header(translate[lang]("2. SOS Emergency Alert"))
if st.button("Send SOS"):
    db.collection("sos_alerts").add({
        "username": st.secrets["firebase"]["client_email"],
        "location": firestore.GeoPoint(latitude, longitude),
        "timestamp": firestore.SERVER_TIMESTAMP,
    })
    st.success("SOS Sent!")

# Fish prediction dummy
st.header(translate[lang]("4. AI-Based Fish Catch Prediction"))
pred = random.choice(["High Chances", "Moderate Chances", "Low Chances"])
st.metric(label="Prediction", value=translate[lang](pred))

# Fish logging
st.header(translate[lang]("5. Log Fish Catch"))
with st.form("catch_form"):
    fish_type = st.text_input("Fish Type")
    weight = st.number_input("Weight (kg)", min_value=0.0)
    date = st.date_input("Date", value=datetime.date.today())
    submitted = st.form_submit_button("Log Catch")
    if submitted:
        db.collection("catches").add({"type": fish_type, "weight": weight, "date": str(date), "loc": [latitude, longitude]})
        st.success("Catch Logged")

# Voice alert
st.header(translate[lang]("6. Voice Alerts"))
if latitude > 8.5:
    speak(translate[lang]("You are near a danger zone!"), lang='ta' if lang == "தமிழ்" else 'en')

# Safe route planning placeholder
st.header(translate[lang]("7. Safe Route Planner"))
st.markdown("Safe route from your location is being processed... (dummy)")

# Community fish zones
st.header(translate[lang]("8. Community Shared Fish Zones"))
if st.button("Add My Current Location as Good Zone"):
    db.collection("fish_zones").add({"lat": latitude, "lon": longitude})
    st.success("Zone Shared")

# Multilingual
st.header(translate[lang]("10. Multilingual UI"))
st.success(translate[lang]("Current language applied"))

# Emergency Contacts
st.header(translate[lang]("13. Emergency Contacts"))
st.markdown("**Coast Guard:** 1554\n**Emergency:** 112\n**Family Contact:** +91 9876543210")

# Leaderboard (dummy)
st.header(translate[lang]("14. Top Contributors"))
st.table(pd.DataFrame({"User": ["Ravi", "Mani"], "Catches": [23, 17]}))

# Badges (dummy)
st.header(translate[lang]("15. Your Badges"))
st.success("Fishing Master | Safe Sailor")

# Recent alerts
st.header(translate[lang]("16. Recent SOS Alerts"))
alerts = db.collection("sos_alerts").order_by("timestamp", direction=firestore.Query.DESCENDING).limit(5).stream()
for alert in alerts:
    a = alert.to_dict()
    st.write(f"{a['username']} at {a['location'].latitude},{a['location'].longitude}")

# Heatmap (dummy)
st.header(translate[lang]("18. Fish Heatmap"))
heat_df = pd.DataFrame({"lat": [latitude+0.01], "lon": [longitude+0.01], "weight": [5]})
st.map(heat_df)

# Daily tips
st.header(translate[lang]("20. Daily Fishing Tip"))
tips = ["Fish near rocky areas today.", "Avoid strong tides.", "Cast net around 6 AM."]
st.info(random.choice(tips))





