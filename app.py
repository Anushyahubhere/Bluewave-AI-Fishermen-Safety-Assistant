import streamlit as st
import os
import time
import json
from datetime import datetime
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore
from streamlit.components.v1 import iframe

# Load environment variables
load_dotenv()
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
FIREBASE_CRED_PATH = os.getenv("FIREBASE_CRED_PATH")

# Firebase Initialization (optimized for single init)
if not firebase_admin._apps:
    cred = credentials.Certificate(FIREBASE_CRED_PATH)
    firebase_admin.initialize_app(cred)

db = firestore.client()

# Page Config
st.set_page_config(page_title="BlueWave AI", layout="wide")

# Session State
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

# --- Login UI ---
def login():
    with st.sidebar:
        st.subheader("🔒 Login")
        user = st.text_input("Username")
        pwd = st.text_input("Password", type="password")
        if st.button("Login"):
            if user == "fisherman" and pwd == "bluewave123":
                st.session_state["authenticated"] = True
                st.success("✅ Login Successful")
            else:
                st.error("❌ Invalid Credentials")

# Run login logic
if not st.session_state["authenticated"]:
    login()
    st.stop()

# --- Sidebar Controls ---
st.sidebar.title("🧭 Navigation")
lang = st.sidebar.selectbox("Language / மொழி", ["English", "தமிழ்"])
view_mode = st.sidebar.radio("Map View", ["Roadmap", "Satellite"])

# --- GPS Input ---
with st.form("location_form"):
    st.subheader("📍 Real-time Location Input")
    col1, col2 = st.columns(2)
    lat = col1.number_input("Latitude", value=10.5, format="%.6f")
    lon = col2.number_input("Longitude", value=76.2, format="%.6f")
    submitted = st.form_submit_button("Update Location")

# Show location map
if submitted or ("last_lat" not in st.session_state):
    st.session_state["last_lat"] = lat
    st.session_state["last_lon"] = lon

cur_lat = st.session_state["last_lat"]
cur_lon = st.session_state["last_lon"]

map_type = "roadmap" if view_mode == "Roadmap" else "satellite"
map_url = f"https://www.google.com/maps/embed/v1/view?key={GOOGLE_MAPS_API_KEY}&center={cur_lat},{cur_lon}&zoom=10&maptype={map_type}"
iframe(map_url, height=400)

# --- AI Predictions (mocked logic) ---
def get_weather():
    return "🌫️ Cloudy with chances of storm"

def border_alert(lat, lon):
    if 10 <= lat <= 20 and 75 <= lon <= 80:
        return "✅ Inside Safe Zone"
    return "⚠️ Border Alert! Dangerous Area!"

def predict_fish_zone(lat, lon):
    if 10 <= lat <= 13 and 76 <= lon <= 78:
        return "🎣 Good fishing zone detected"
    return "🚫 No active fishing zone nearby"

# --- AI Safety Display ---
st.subheader("🧠 AI Safety Predictions")
st.info(f"Weather: {get_weather()}")
st.warning(f"Border Status: {border_alert(cur_lat, cur_lon)}")
st.success(f"Fish Zone: {predict_fish_zone(cur_lat, cur_lon)}")

# --- SOS Section ---
st.markdown("---")
st.subheader("🚨 Emergency SOS")
if st.button("Send SOS"):
    db.collection("sos_alerts").add({
        "timestamp": datetime.now().isoformat(),
        "location": {"lat": cur_lat, "lon": cur_lon},
        "status": "Emergency"
    })
    st.success("📡 SOS Alert Logged!")

# --- Logbook ---
@st.cache_data(ttl=30)
def get_recent_sos():
    return list(db.collection("sos_alerts")
                .order_by("timestamp", direction=firestore.Query.DESCENDING)
                .limit(10).stream())

st.subheader("📘 Safety Logbook")
for log in get_recent_sos():
    entry = log.to_dict()
    st.write(f"🕒 {entry['timestamp']} | 📍 {entry['location']} | 🚨 {entry['status']}")

# --- Community Tips ---
@st.cache_data(ttl=30)
def get_community_tips():
    return list(db.collection("safety_tips").stream())

st.markdown("---")
st.subheader("💡 Community Safety Tips")

with st.expander("➕ Submit Tip"):
    tip = st.text_area("Write your tip (English or Tamil):")
    if st.button("Submit Tip"):
        db.collection("safety_tips").add({
            "tip": tip,
            "time": time.ctime()
        })
        st.success("📝 Tip Submitted!")

for t in get_community_tips():
    st.markdown(f"🔹 {t.to_dict()['tip']}")

# --- Gemini Chatbot Placeholder ---
st.markdown("---")
st.subheader("🤖 Gemini AI Assistant")
user_input = st.text_input("Ask something:")
if st.button("Ask Gemini"):
    st.info("Gemini: This is a placeholder. Add Vertex AI integration for real chatbot.")

# --- Footer ---
st.markdown("---")
st.caption("© 2025 BlueWave AI | Powered by Streamlit, Firebase, Google Maps")




