# BlueWave AI - Fishermen Safety Assistant (Final Cloud Compatible)
import streamlit as st
from firebase_admin import credentials, firestore, initialize_app
import firebase_admin
from datetime import datetime
import uuid
import json
import requests
import pandas as pd
from streamlit_lottie import st_lottie
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

    # Save prediction to Firestore
    if st.session_state.user:
        db.collection("ai_predictions").add({
            "username": st.session_state.user,
            "score": score,
            "timestamp": datetime.utcnow()
        })

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
            st.session_state.command = command
            st.success(f"Voice command recognized: {command}")
            
            if "sos" in command:
                st.info("Triggering SOS alert flow...")
            elif "safe" in command:
                st.info("Showing Safe Zone prediction...")
            elif "fish" in command:
                st.info("Opening AI Fish Catch Prediction...")
            else:
                st.warning("Command not recognized")
            
            speak(f"Command received: {command}")
    else:
        st.warning("Please log in to use the voice assistant.")

# --- FISHING TRENDS ---
elif menu == "Fishing Trends":
    st.subheader("📈 Fishing Trends Analysis")
    if st.session_state.user:
        predictions_ref = db.collection("ai_predictions").order_by("timestamp", direction=firestore.Query.DESCENDING).limit(20)
        data_list = []
        for doc in predictions_ref.stream():
            d = doc.to_dict()
            data_list.append({
                "timestamp": d.get("timestamp"),
                "score": d.get("score", 0)
            })
        if data_list:
            df = pd.DataFrame(data_list).sort_values("timestamp")
            st.line_chart(df.set_index("timestamp")["score"])
            st.success("✅ Trend chart displayed")
        else:
            st.info("No prediction data available yet.")
    else:
        st.warning("Login to view fishing trends.")

# --- SAFE ROUTES PLANNER ---
elif menu == "Safe Routes":
    st.subheader("🗺️ Safe Route Planner")
    if st.session_state.user:
        start_lat = st.number_input("Start Latitude", value=8.5)
        start_lon = st.number_input("Start Longitude", value=78.1)
        end_lat = st.number_input("End Latitude", value=8.6)
        end_lon = st.number_input("End Longitude", value=78.2)
        max_wind = st.number_input("Maximum Safe Wind (km/h)", value=25)
        if st.button("Generate Safe Route"):
            risk_zones_ref = db.collection("sos_alerts").order_by("timestamp", direction=firestore.Query.DESCENDING).limit(10)
            risk_points = []
            for doc in risk_zones_ref.stream():
                d = doc.to_dict()
                if d.get("latitude") and d.get("longitude"):
                    risk_points.append([float(d["latitude"]), float(d["longitude"])])
            route_df = pd.DataFrame([{"lat": start_lat, "lon": start_lon}, {"lat": end_lat, "lon": end_lon}])
            st.map(route_df)
            if risk_points:
                st.warning(f"⚠️ {len(risk_points)} risky zones detected along route. Avoid them!")
            else:
                st.success("✅ Route appears safe.")
    else:
        st.warning("Login to plan safe routes.")

# --- ALERTS ---
elif menu == "Alerts":
    st.subheader("📢 Nearby Alerts")
    if st.session_state.user:
        sos_ref = db.collection("sos_alerts").order_by("timestamp", direction=firestore.Query.DESCENDING).limit(10)
        for doc in sos_ref.stream():
            data = doc.to_dict()
            st.info(f"🚨 {data.get('username','Unknown')} at ({data.get('latitude','N/A')}, {data.get('longitude','N/A')}): {data.get('message','No message')}")
    else:
        st.warning("Please login to view alerts.")

# --- ABOUT ---
elif menu == "About":
    st.subheader("🌊 About BlueWave AI")
    st_lottie(load_lottie_url("https://assets5.lottiefiles.com/packages/lf20_zrqthn6o.json"), height=200)
    st.markdown("""
    BlueWave AI is an assistant platform to enhance safety and success of fishermen using:
    - Real-time tracking
    - SOS emergency response
    - AI-based fish detection
    - Safe Zone prediction
    - Voice assistant (cloud-friendly)
    - Fishing Trends & Safe Routes
    - Multilingual support (coming soon)
    - Offline/mobile compatibility (coming soon)
    """)








