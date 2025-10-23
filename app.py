# BlueWave AI - Fishermen Safety Assistant
import streamlit as st
from firebase_admin import credentials, firestore, initialize_app
import firebase_admin
from datetime import datetime
import uuid
import json
import requests
from streamlit_lottie import st_lottie

# Streamlit setup
st.set_page_config(page_title="BlueWave AI", layout="wide")
st.title("🌊 BlueWave AI - Fishermen Safety Assistant")

# Firebase setup
if not firebase_admin._apps:
    cred = credentials.Certificate(dict(st.secrets["firebase"]))
    initialize_app(cred)

db = firestore.client()

# Lottie loader
def load_lottie_url(url):
    try:
        r = requests.get(url)
        if r.status_code == 200:
            return r.json()
    except:
        return None

# --- Sidebar Navigation ---
menu = st.sidebar.radio(
    "📱 Navigation",
    [
        "Login",
        "Send SOS",
        "AI Prediction",
        "Weather Advisory",
        "Community Updates",
        "Alerts",
        "About",
    ],
)
st.sidebar.markdown("---")
st.sidebar.markdown("Made with ❤️ for Fishermen")

# --- Session State ---
if "user" not in st.session_state:
    st.session_state.user = None

# --- LOGIN PAGE ---
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

# --- SOS FEATURE ---
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
    else:
        st.warning("Please login to send an SOS alert.")

# --- AI PREDICTION FEATURE ---
elif menu == "AI Prediction":
    st.subheader("🤖 AI Fish Catch Prediction")
    st.markdown("Upload data for fish catch prediction (e.g., temperature, salinity, etc.)")

    uploaded_file = st.file_uploader("Upload JSON file", type=["json"])
    if uploaded_file:
        data = json.load(uploaded_file)
        # Placeholder for prediction logic
        score = 0.68
        st.success(f"🎯 Predicted Fish Availability Score: {score * 100:.1f}%")
        st.progress(int(score * 100))
        st.caption("This is an experimental AI-based estimate.")

# --- WEATHER ADVISORY FEATURE ---
elif menu == "Weather Advisory":
    st.subheader("🌤 Sea Condition & Weather Advisory")

    st.markdown("Enter your fishing area to get live sea safety status:")
    place = st.text_input("Location (e.g., Chennai, Rameswaram)")

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
            else:
                st.success("✅ Sea condition safe for fishing.")
        except Exception as e:
            st.error("Unable to fetch weather data. Try again later.")

# --- COMMUNITY UPDATES FEATURE ---
elif menu == "Community Updates":
    st.subheader("💬 Fishermen Community Forum")

    if st.session_state.user:
        st.markdown("Share updates, fish catches, or local information:")
        post = st.text_area("Your update message")

        if st.button("Post Update"):
            post_id = str(uuid.uuid4())
            db.collection("community_updates").document(post_id).set({
                "username": st.session_state.user,
                "post": post,
                "timestamp": datetime.utcnow()
            })
            st.success("✅ Post shared successfully!")

        st.markdown("### 🌍 Recent Updates")
        updates = db.collection("community_updates").order_by(
            "timestamp", direction=firestore.Query.DESCENDING
        ).limit(10)

        for doc in updates.stream():
            u = doc.to_dict()
            st.info(f"**{u['username']}**: {u['post']}  \n🕒 {u['timestamp']}")
    else:
        st.warning("Please login to post or view community updates.")

# --- ALERTS FEATURE ---
elif menu == "Alerts":
    st.subheader("📢 Recent SOS Alerts")

    alerts = db.collection("sos_alerts").order_by(
        "timestamp", direction=firestore.Query.DESCENDING
    ).limit(10)

    for doc in alerts.stream():
        data = doc.to_dict()
        st.warning(
            f"🚨 **{data.get('username', 'Unknown')}** reported: {data.get('message', '')}\n"
            f"📍 Location: {data.get('latitude', 'N/A')}, {data.get('longitude', 'N/A')}\n"
            f"🕒 {data.get('timestamp')}"
        )

# --- ABOUT PAGE ---
elif menu == "About":
    st.subheader("🌊 About BlueWave AI")
    st_lottie(load_lottie_url("https://assets5.lottiefiles.com/packages/lf20_zrqthn6o.json"), height=200)
    st.markdown("""
    **BlueWave AI** is an innovative safety assistant for fishermen powered by AI & cloud.
    
    ### 🌟 Features:
    - 🚨 SOS Emergency Alerts  
    - 🤖 AI Fish Catch Prediction  
    - 🌤 Weather & Sea Safety Advisory  
    - 💬 Fishermen Community Forum  
    - 📢 Real-time Alerts System  
    - 🈁 Multilingual Support (Coming Soon)
    
    Made with ❤️ by Team BlueWave for safe and smart fishing.
    """)
