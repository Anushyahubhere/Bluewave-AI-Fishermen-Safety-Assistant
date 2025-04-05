import streamlit as st
import pyttsx3
import requests
import firebase_admin
from firebase_admin import credentials, firestore
import time
import json

# Firebase Setup
cred = credentials.Certificate("bluewave-ai-34bdc-firebase-adminsdk-fbsvc-1a6c809736.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# Google Cloud API Key
GOOGLE_MAPS_API_KEY = "AIzaSyDTGMq-2U1N6nh98TCr_PFFXrW3mEkWmOI"

# Voice Engine
engine = pyttsx3.init()
engine.setProperty('rate', 150)

# Language Toggle
lang = st.sidebar.selectbox("Choose Language / மொழியைத் தேர்ந்தெடுக்கவும்", ["English", "தமிழ்"])

# Function to speak text
def speak(text):
    engine.say(text)
    engine.runAndWait()

# Dummy Fish Zone Prediction
def predict_fish_zone(lat, lon):
    if 9 < lat < 11 and 75 < lon < 77:
        return "High Fish Density Zone"
    return "Low Fish Probability"

# Dummy Border Alert
def border_alert(lat, lon):
    if 10 < lat < 20 and 75 < lon < 80:
        return "Inside Safe Zone"
    return "Border Alert! Return immediately!"

# Dummy Weather from Google Cloud API (simulate)
def get_weather():
    return "Cloudy with slight rain"

# Dummy Route Optimization (simulate)
def get_optimized_route():
    return "Route: Port > Mid Sea > Fish Zone > Return"

# Send SOS to Firebase
def send_sos(location):
    db.collection("sos_alerts").add({
        "timestamp": time.ctime(),
        "location": location
    })
    st.success("SOS sent and logged!")

# UI Styling
st.markdown("""
    <style>
    .main {
        background-color: #e3f2fd;
        padding: 20px;
        border-radius: 15px;
    }
    </style>
""", unsafe_allow_html=True)

# Title
if lang == "English":
    st.title("BlueWave AI - Fishermen Safety Assistant")
else:
    st.title("புளூவேவ் ஏஐ - மீனவர்களின் பாதுகாப்பு உதவியாளர்")

# Inputs
st.subheader("Location Input")
lat = st.number_input("Latitude", value=10.5)
lon = st.number_input("Longitude", value=76.2)
view_mode = st.radio("Map View Mode", ["roadmap", "satellite"])

# Predictions
weather = get_weather()
border = border_alert(lat, lon)
fish_zone = predict_fish_zone(lat, lon)
route = get_optimized_route()

# Speak Alert
if st.button("Voice Safety Alert"):
    if lang == "English":
        speak(f"Weather: {weather}. Border: {border}. Fish: {fish_zone}")
    else:
        speak(f"மழை நிலை: {weather}. எல்லை: {border}. மீன் நிலை: {fish_zone}")

# Map Display
st.subheader("Live Map")
map_url = f"https://www.google.com/maps/embed/v1/view?key={GOOGLE_MAPS_API_KEY}&center={lat},{lon}&zoom=10&maptype={view_mode}"
st.components.v1.iframe(map_url, height=400)

# Results Display
st.subheader("AI Safety Predictions")
st.info(f"Weather: {weather}")
st.warning(f"Border Alert: {border}")
st.success(f"Fish Zone: {fish_zone}")
st.caption(f"Optimized Route: {route}")

# SOS Button
if st.button("Send Emergency SOS"):
    send_sos({"lat": lat, "lon": lon})

# Footer
st.markdown("---")
st.caption("Powered by Streamlit | Firebase | Google Cloud | Gemini")
