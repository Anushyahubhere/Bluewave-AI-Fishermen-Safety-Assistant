# BlueWave AI - Fishermen Safety Assistant
mport streamlit as st
from firebase_admin import credentials, firestore, initialize_app
import firebase_admin
from datetime import datetime
import uuid
import json
import requests
from streamlit_lottie import st_lottie

# Set Streamlit config
st.set_page_config(page_title="BlueWave AI", layout="wide")
st.title("🌊 BlueWave AI - Fishermen Safety Assistant")

# Load Firebase credentials
if not firebase_admin._apps:
    cred = credentials.Certificate(dict(st.secrets["firebase"]))
    initialize_app(cred)

db = firestore.client()

# Load Lottie animation (optional)
def load_lottie_url(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# --- Sidebar ---
menu = st.sidebar.radio("📱 Navigation", ["Login", "Real-time Location", "Send SOS", "Fish Zones", "AI Prediction", "Alerts", "About"])
st.sidebar.markdown("---")
st.sidebar.markdown("Made with ❤️ for Fishermen")

# --- Session State ---
if "user" not in st.session_state:
    st.session_state.user = None

# --- Login ---
if menu == "Login":
    st.subheader("🔐 Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        user_ref = db.collection("users").document(username).get()
        if user_ref.exists and user_ref.to_dict().get("password") == password:
            st.success("Logged in successfully!")
            st.session_state.user = username
        else:
            st.error("Invalid username or password")

# --- Real-time Location Map ---
elif menu == "Real-time Location":
    st.subheader("📍 Real-time Fisherman Location")
    if st.session_state.user:
        lat = st.number_input("Latitude", value=8.5)
        lon = st.number_input("Longitude", value=78.1)
        if st.button("Update Location"):
            db.collection("locations").document(st.session_state.user).set({
                "username": st.session_state.user,
                "latitude": lat,
                "longitude": lon,
                "timestamp": datetime.utcnow()
            })
            st.success("Location updated")
        map_url = f"https://www.google.com/maps/embed/v1/view?key={st.secrets['GOOGLE_MAPS_API_KEY']}&center={lat},{lon}&zoom=10&maptype=satellite"
        st.components.v1.iframe(map_url, height=500, width=800)
    else:
        st.warning("Please log in to access location features")

# --- SOS Feature ---
elif menu == "Send SOS":
    st.subheader("🚨 Send Emergency SOS")
    if st.session_state.user:
        emergency_msg = st.text_area("Describe the emergency")
        lat = st.number_input("Latitude", value=8.5, key="sos_lat")
        lon = st.number_input("Longitude", value=78.1, key="sos_lon")
        if st.button("Send SOS"):
            db.collection("sos_alerts").add({
                "username": st.session_state.user,
                "message": emergency_msg,
                "latitude": lat,
                "longitude": lon,
                "timestamp": datetime.utcnow()
            })
            st.success("SOS Alert Sent!")
    else:
        st.warning("Please log in to send an SOS")

# --- Fish Detection Zones ---
elif menu == "Fish Zones":
    st.subheader("🐟 Fish Detection Zones")
    st.markdown("**Predicted Hotspots for Fish**")
    # Overlay from static map or external data (placeholder)
    fish_map_url = f"https://www.google.com/maps/embed/v1/search?key={st.secrets['GOOGLE_MAPS_API_KEY']}&q=fish+zones+in+Tamil+Nadu"
    st.components.v1.iframe(fish_map_url, height=500, width=800)

# --- AI Prediction (Placeholder logic) ---
elif menu == "AI Prediction":
    st.subheader("🤖 AI Fish Catch Prediction")
    st.markdown("Upload environmental data for prediction")
    uploaded_file = st.file_uploader("Upload JSON with water temp, salinity, etc.")
    if uploaded_file:
        data = json.load(uploaded_file)
        score = 0.7  # Dummy model
        st.success(f"✅ Predicted Fish Availability Score: {score * 100:.1f}%")

# --- Location-based Alerts ---
elif menu == "Alerts":
    st.subheader("📢 Nearby Alerts")
    if st.session_state.user:
        user_loc = db.collection("locations").document(st.session_state.user).get()
        if user_loc.exists:
            u_data = user_loc.to_dict()
            sos_ref = db.collection("sos_alerts").order_by("timestamp", direction=firestore.Query.DESCENDING).limit(10)
            for doc in sos_ref.stream():
                data = doc.to_dict()
                st.info(f"🚨 {data.get('username', 'Unknown')} at ({data.get('latitude', 'N/A')}, {data.get('longitude', 'N/A')}): {data.get('message', 'No message')}")

        else:
            st.warning("No location info found")
    else:
        st.warning("Please login to view alerts")

# --- About ---
elif menu == "About":
    st.subheader("🌊 About BlueWave AI")
    st_lottie(load_lottie_url("https://assets5.lottiefiles.com/packages/lf20_zrqthn6o.json"), height=200)
    st.markdown("""
    BlueWave AI is an assistant platform to enhance safety and success of fishermen using:
    - Real-time tracking
    - SOS emergency response
    - AI-based fish detection
    - Multilingual support (coming soon)
    - Offline/mobile compatibility (coming soon)
    """)
