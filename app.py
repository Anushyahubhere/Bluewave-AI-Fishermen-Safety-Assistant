# BlueWave AI - Fishermen Safety Assistant
import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import pydeck as pdk
from datetime import datetime
import json
import base64
import time

# --- Page config ---
st.set_page_config("BlueWave AI - Fishermen Safety Assistant", layout="wide")

# --- Multilingual support ---
languages = {"English": "en", "தமிழ்": "ta"}
lang = st.sidebar.radio("Language / மொழி", list(languages.keys()))

# --- Language text mapping ---
TEXT = {
    "login_title": {"en": "Login", "ta": "உள்நுழை"},
    "username": {"en": "Username", "ta": "பயனர்பெயர்"},
    "password": {"en": "Password", "ta": "கடவுச்சொல்"},
    "login_button": {"en": "Login", "ta": "உள்நுழைய"},
    "logout_button": {"en": "Logout", "ta": "வெளியேறு"},
    "map_title": {"en": "Fishing Zone Map", "ta": "வலை வீசும் பகுதிகள்"},
    "sos_button": {"en": "Send SOS", "ta": "அவசரக் கோரிக்கை அனுப்பு"},
    "fish_log": {"en": "Log Fish Catch", "ta": "மீன் பிடிப்பு பதிவு"},
    "route_plan": {"en": "Safe Route Plan", "ta": "பாதுகாப்பான பாதை திட்டம்"}
}

# --- Firebase Init ---
if not firebase_admin._apps:
    cred = credentials.Certificate(st.secrets["firebase"])
    firebase_admin.initialize_app(cred)
db = firestore.client()

# --- Session state ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# --- Login ---
def login_ui():
    st.title(TEXT["login_title"][languages[lang]])
    username = st.text_input(TEXT["username"][languages[lang]])
    password = st.text_input(TEXT["password"][languages[lang]], type="password")
    if st.button(TEXT["login_button"][languages[lang]]):
        users_ref = db.collection("users").where("username", "==", username).stream()
        user_doc = next(users_ref, None)
        if user_doc and user_doc.to_dict().get("password") == password:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success("✅ Logged in successfully!")
        else:
            st.error("❌ Invalid credentials.")

# --- Logout ---
def logout_ui():
    if st.button(TEXT["logout_button"][languages[lang]]):
        st.session_state.logged_in = False
        st.experimental_rerun()

# --- SOS ---
def sos_ui():
    if st.button(TEXT["sos_button"][languages[lang]]):
        location = st.session_state.get("current_location", {"lat": 0, "lon": 0})
        db.collection("sos").add({
            "username": st.session_state.username,
            "location": location,
            "timestamp": datetime.utcnow()
        })
        st.warning("🚨 SOS sent to rescue team!")

# --- GPS Input ---
def gps_input():
    st.sidebar.subheader("📍 GPS Location")
    lat = st.sidebar.number_input("Latitude", format="%f", value=9.0)
    lon = st.sidebar.number_input("Longitude", format="%f", value=79.0)
    st.session_state.current_location = {"lat": lat, "lon": lon}

# --- Fish Log ---
def fish_log_ui():
    st.subheader(TEXT["fish_log"][languages[lang]])
    fish_type = st.text_input("Fish Type")
    weight = st.number_input("Weight (kg)", min_value=0.0)
    if st.button("Submit Log"):
        db.collection("fish_logs").add({
            "user": st.session_state.username,
            "type": fish_type,
            "weight": weight,
            "location": st.session_state.get("current_location", {}),
            "timestamp": datetime.utcnow()
        })
        st.success("🐟 Catch logged!")

# --- Map ---
def map_ui():
    st.subheader(TEXT["map_title"][languages[lang]])
    location = st.session_state.get("current_location", {"lat": 9.0, "lon": 79.0})
    map_data = [{"lat": location["lat"], "lon": location["lon"]}]
    st.map(map_data)

# --- Main App ---
if not st.session_state.logged_in:
    login_ui()
else:
    logout_ui()
    gps_input()
    map_ui()
    sos_ui()
    fish_log_ui()
    st.sidebar.write("🌐 Version: 1.0")
    st.sidebar.write("🔒 Logged in as:", st.session_state.username)
