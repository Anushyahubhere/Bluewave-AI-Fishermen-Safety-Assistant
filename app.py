import streamlit as st
import requests
import json
import firebase_admin
from firebase_admin import credentials, firestore
import time

# Load Firebase credentials (make sure the JSON file is in the same folder)
cred = credentials.Certificate("bluewave-ai-34bdc-firebase-adminsdk-fbsvc-1a6c809736.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# Google Maps API key
GOOGLE_MAPS_API_KEY = "AIzaSyDTGMq-2U1N6nh98TCr_PFFXrW3mEkWmOI"

# Simulated Weather Prediction
def get_weather(lat, lon):
    return "Sunny with waves, 20% chance of storm"

# Simulated Fish Zone Prediction
def predict_fish_zone(lat, lon):
    if 8 < lat < 20 and 70 < lon < 85:
        return "High Fish Density Zone"
    return "Low Fish Activity"

# Simulated Border Alert
def border_alert(lat, lon):
    if 10 < lat < 20 and 75 < lon < 80:
        return "Inside Safe Zone"
    return "Border Alert! Return immediately!"

# SOS Logger
def send_sos(location):
    db.collection("sos_alerts").add({
        "timestamp": time.ctime(),
        "location": location
    })
    st.success("SOS sent and logged!")

# Background image from Unsplash
st.markdown("""
    <style>
    .stApp {
        background-image: url("https://images.unsplash.com/photo-1507525428034-b723cf961d3e");
        background-size: cover;
        background-attachment: fixed;
        color: black;
    }
    </style>
""", unsafe_allow_html=True)

# Language switch
lang = st.sidebar.selectbox("Choose Language / மொழியைத் தேர்ந்தெடுக்கவும்", ["English", "தமிழ்"])

# App title
st.title("BlueWave AI - Fishermen Safety Assistant" if lang == "English" else "புளூவேவ் ஏஐ - மீனவர்களின் பாதுகாப்பு உதவியாளர்")

# Input
st.subheader("Enter Location Coordinates")
lat = st.number_input("Latitude", value=10.5)
lon = st.number_input("Longitude", value=76.2)

# Data processing
weather = get_weather(lat, lon)
border = border_alert(lat, lon)
fish_zone = predict_fish_zone(lat, lon)

# Live Map
st.subheader("Live Map View")
map_mode = st.selectbox("Select Map Type", ["roadmap", "satellite"])
map_url = f"https://www.google.com/maps/embed/v1/view?key={GOOGLE_MAPS_API_KEY}&center={lat},{lon}&zoom=10&maptype={map_mode}"
st.components.v1.iframe(map_url, height=400)

# Predictions
st.subheader("AI Safety Prediction")
st.info(f"Weather Update: {weather}")
st.warning(f"Border Status: {border}")
st.success(f"Fish Zone: {fish_zone}")

# Route directions
st.subheader("Route Optimization")
route_url = f"https://www.google.com/maps/dir/?api=1&destination={lat},{lon}"
st.markdown(f"[Get Route Directions]({route_url})", unsafe_allow_html=True)

# SOS button
if st.button("Send Emergency SOS"):
    send_sos({"lat": lat, "lon": lon})

# Footer
st.markdown("---")
st.caption("Powered by Streamlit | Firebase | Google Cloud | GDG Hackathon")



