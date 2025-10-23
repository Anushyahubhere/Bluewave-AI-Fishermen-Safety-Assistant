# BlueWave AI - Fishermen Safety Assistant (Advanced & Cloud Compatible)
import streamlit as st
from firebase_admin import credentials, firestore, initialize_app
import firebase_admin
from datetime import datetime
import uuid
import json
import requests
from streamlit_lottie import st_lottie
import pandas as pd
from streamlit_js_eval import streamlit_js_eval

# --- Streamlit Setup ---
st.set_page_config(page_title="BlueWave AI", layout="wide")
st.title("🌊 BlueWave AI - Fishermen Safety Assistant (Cloud Compatible)")

# --- Firebase Setup ---
if not firebase_admin._apps:
    cred = credentials.Certificate(dict(st.secrets["firebase"]))
    initialize_app(cred)
db = firestore.client()

# --- Lottie Loader ---
def load_lottie_url(url):
    try:
        r = requests.get(url)
        if r.status_code == 200:
            return r.json()
    except:
        return None

# --- Browser TTS ---
def speak(text):
    st.components.v1.html(f"""
        <script>
            var msg = new SpeechSynthesisUtterance("{text}");
            window.speechSynthesis.speak(msg);
        </script>
        """, height=0)

# --- Browser-safe voice input ---
def get_browser_voice_command():
    st.info("🎤 Enter your command here (simulate voice input)")
    command = st.text_input("Voice Command (type what you would speak)")
    return command.lower() if command else ""

# --- Sidebar Navigation ---
menu = st.sidebar.radio(
    "📱 Navigation",
    [
        "Login",
        "Send SOS",
        "AI Prediction",
        "Weather Advisory",
        "Community Updates",
        "Real-time Location",
        "Safe Zone Prediction",
        "Voice Assistant",
        "Fishing Trends",
        "Safe Routes",
        "Alerts",
        "About",
    ],
)
st.sidebar.markdown("---")
st.sidebar.markdown("Made with ❤️ for Fishermen")

# --- Session State ---
if "user" not in st.session_state:
    st.session_state.user = None

# --- LOGIN ---
if menu == "Login":
    st.subheader("🔐 Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        user_ref = db.collection("users").document(username).get()
        if user_ref.exists and user_ref.to_dict().get("password") == password:
            st.session_state.user = username
            st.success(f"Welcome back, {username}!")
        else:
            st.error("Invalid username or password")

# --- SEND SOS ---
elif menu == "Send SOS":
    st.subheader("🚨 Emergency SOS Alert")
    if st.session_state.user:
        msg = st.text_area("Describe the emergency")
        lat = st.text_input("Latitude (optional)")
        lon = st.text_input("Longitude (optional)")
        if st.button("Send SOS"):
            sos_id = str(uuid.uuid4())
            db.collection("sos_alerts").document(sos_id).set({
                "username": st.session_state.user,
                "message": msg,
                "latitude": lat,
                "longitude": lon,
                "timestamp": datetime.utcnow()
            })
            st.success("✅ SOS alert sent successfully!")
            speak("SOS alert sent successfully")
    else:
        st.warning("Please login to send an SOS alert.")

# --- AI PREDICTION ---
elif menu == "AI Prediction":
    st.subheader("🤖 AI Fish Catch Prediction")
    st.markdown("Upload environmental data (JSON) or enter manually:")

    # Default values
    default_data = {
        "water_temp": 28,
        "salinity": 35,
        "ph": 7.5,
        "wind_speed": 10,
        "tide": 1.5,
        "time_of_day": "morning"
    }

    uploaded_file = st.file_uploader("Upload JSON file", type=["json"])
    if uploaded_file:
        try:
            json_data = json.load(uploaded_file)
            for key in default_data:
                if key in json_data:
                    default_data[key] = json_data[key]
            st.success("✅ JSON loaded successfully!")
        except:
            st.error("⚠️ Invalid JSON file")

    # Manual input fields
    water_temp = st.number_input("Water Temperature (°C)", value=float(default_data["water_temp"]))
    salinity = st.number_input("Salinity (ppt)", value=float(default_data["salinity"]))
    ph = st.number_input("pH Level", value=float(default_data["ph"]))
    wind_speed = st.number_input("Wind Speed (km/h)", value=float(default_data["wind_speed"]))
    tide = st.number_input("Tide Level (m)", value=float(default_data["tide"]))
    time_of_day = st.selectbox("Time of Day", ["morning", "afternoon", "evening"], index=["morning","afternoon","evening"].index(default_data["time_of_day"]))

    # Calculate weighted score
    time_factor = {"morning":0.3, "afternoon":0.2, "evening":0.1}[time_of_day]
    score = (
        0.3 * (1 - abs(water_temp - 28)/10) +
        0.2 * (1 - abs(salinity - 35)/10) +
        0.2 * (1 - abs(ph - 7.5)/2) +
        0.1 * (1 - wind_speed/50) +
        0.1 * (1 - abs(tide - 1.5)/2) +
        0.1 * time_factor
    )
    score = max(0, min(1, score))
    st.success(f"🎯 Predicted Fish Availability Score: {score*100:.1f}%")
    st.progress(int(score*100))

    # Contribution chart
    contributions = {
        "Temperature": 0.3 * (1 - abs(water_temp - 28)/10),
        "Salinity": 0.2 * (1 - abs(salinity - 35)/10),
        "pH": 0.2 * (1 - abs(ph - 7.5)/2),
        "Wind": 0.1 * (1 - wind_speed/50),
        "Tide": 0.1 * (1 - abs(tide - 1.5)/2),
        "Time of Day": 0.1 * time_factor
    }
    df_contrib = pd.DataFrame(list(contributions.items()), columns=["Factor", "Contribution"])
    st.bar_chart(df_contrib.set_index("Factor"))

    # Browser TTS
    speak(f"Predicted fish availability score is {score*100:.0f} percent")

# --- WEATHER ADVISORY ---
elif menu == "Weather Advisory":
    st.subheader("🌤 Sea Condition & Weather Advisory")
    place = st.text_input("Enter location (e.g., Chennai)")
    if st.button("Check Advisory"):
        try:
            url = f"https://wttr.in/{place}?format=j1"
            res = requests.get(url).json()
            current = res["current_condition"][0]
            temp = current["temp_C"]
            wind = current["windspeedKmph"]
            weather = current["weatherDesc"][0]["value"]
            st.metric("Temperature", f"{temp}°C")
            st.metric("Wind Speed", f"{wind} km/h")
            st.info(f"🌦️ Current Condition: {weather}")
            if float(wind) > 25:
                st.error("⚠️ Sea condition unsafe! Avoid fishing now.")
                speak("Warning! Sea conditions unsafe.")
            else:
                st.success("✅ Sea condition safe for fishing.")
                speak("Sea conditions are safe for fishing.")
        except:
            st.error("Unable to fetch weather data.")

# --- COMMUNITY UPDATES ---
elif menu == "Community Updates":
    st.subheader("💬 Fishermen Community Forum")
    if st.session_state.user:
        post = st.text_area("Share update / catch / info")
        if st.button("Post Update"):
            post_id = str(uuid.uuid4())
            db.collection("community_updates").document(post_id).set({
                "username": st.session_state.user,
                "post": post,
                "timestamp": datetime.utcnow()
            })
            st.success("✅ Post shared!")
        st.markdown("### 🌍 Recent Updates")
        updates = db.collection("community_updates").order_by(
            "timestamp", direction=firestore.Query.DESCENDING
        ).limit(10)
        for doc in updates.stream():
            u = doc.to_dict()
            st.info(f"**{u.get('username','Unknown')}**: {u.get('post','')}  \n🕒 {u.get('timestamp','')}")
    else:
        st.warning("Login to post or view updates.")

# --- REAL-TIME LOCATION ---
elif menu == "Real-time Location":
    st.subheader("📍 Real-time Location Tracker")
    if st.session_state.user:
        coords = streamlit_js_eval(
            js_expressions="""
            new Promise((resolve, reject) => {
                navigator.geolocation.getCurrentPosition(
                    (pos) => resolve([pos.coords.latitude, pos.coords.longitude]),
                    (err) => resolve(null)
                );
            });
            """,
            key="get_location"
        )
        if coords:
            lat, lon = coords
            st.success(f"✅ Latitude: {lat}, Longitude: {lon}")
            if st.button("Update Location in System"):
                db.collection("locations").document(st.session_state.user).set({
                    "username": st.session_state.user,
                    "latitude": lat,
                    "longitude": lon,
                    "timestamp": datetime.utcnow()
                })
                st.success("📍 Location updated successfully!")
        else:
            st.info("Allow browser to access your location.")
    else:
        st.warning("Login to use location feature.")

# --- SAFE ZONE PREDICTION ---
elif menu == "Safe Zone Prediction":
    st.subheader("🗺️ AI-Based Safe Zone Prediction")
    location = st.text_input("Enter your fishing location")
    wind = st.number_input("Current wind speed (km/h)")
    past_sos_count = st.number_input("Number of past SOS events in this area", value=0)
    if st.button("Predict Safe Zone"):
        risk_score = wind * 0.4 + past_sos_count * 0.6
        if risk_score < 20:
            st.success("✅ Safe Zone")
            st.map(pd.DataFrame({"lat":[10.0], "lon":[78.0]}))
            speak("This zone is safe for fishing")
        else:
            st.error("⚠️ High Risk Zone")
            st.map(pd.DataFrame({"lat":[10.0], "lon":[78.0]}))
            speak("Warning! This zone is risky. Avoid fishing.")

# --- VOICE ASSISTANT ---
elif menu == "Voice Assistant":
    st.subheader("🎤 Voice Assistant")
    if st.session_state.user:
        command = get_browser_voice_command()
        if command:
            if "sos" in command:
                st.session_state.command =






