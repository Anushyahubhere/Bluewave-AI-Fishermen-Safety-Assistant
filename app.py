# BlueWave AI - Fishermen Safety Assistant (Full Advanced + Multilingual)
import streamlit as st
from firebase_admin import credentials, firestore, initialize_app
import firebase_admin
from datetime import datetime
import uuid
import json
import requests
import pandas as pd
from streamlit_lottie import st_lottie

# --- Streamlit Setup ---
st.set_page_config(page_title="BlueWave AI", layout="wide")

# --- Language Selector ---
lang = st.sidebar.selectbox(
    "🌐 Select Language / மொழி / భాష / भाषा",
    ["English", "Hindi", "Tamil", "Telugu"]
)

# --- Translations Dictionary ---
translations = {
    "title": {
        "English": "🌊 BlueWave AI - Fishermen Safety Assistant",
        "Hindi": "🌊 ब्लूवेव एआई - मछुआरों के लिए सुरक्षा सहायक",
        "Tamil": "🌊 புளூவேவ் ஏ.ஐ - மீனவர்களின் பாதுகாப்பு உதவி",
        "Telugu": "🌊 బ్లూవేవ్ ఎ.ఐ - మత్స్యకారుల భద్రతా సహాయకుడు"
    },
    "login": {
        "English": "🔐 Login",
        "Hindi": "🔐 लॉगिन",
        "Tamil": "🔐 உள்நுழைவு",
        "Telugu": "🔐 లాగిన్"
    },
    "username": {"English":"Username","Hindi":"उपयोगकर्ता नाम","Tamil":"பயனர்பெயர்","Telugu":"వాడుకరి పేరు"},
    "password": {"English":"Password","Hindi":"पासवर्ड","Tamil":"கடவுச்சொல்","Telugu":"పాస్వర్డ్"},
    "send_sos": {"English":"🚨 Send Emergency SOS","Hindi":"🚨 आपातकालीन SOS भेजें","Tamil":"🚨 அவசர SOS அனுப்பு","Telugu":"🚨 అత్యవసర SOS పంపండి"},
    "alerts": {"English":"📢 Nearby Alerts","Hindi":"📢 पास के अलर्ट","Tamil":"📢 அருகிலுள்ள எச்சரிக்கைகள்","Telugu":"📢 సమీప హెచ్చరికలు"},
    "about": {"English":"🌊 About BlueWave AI","Hindi":"🌊 ब्लूवेव एआई के बारे में","Tamil":"🌊 புளூவேவ் ஏ.ஐ பற்றி","Telugu":"🌊 బ్లూవేవ్ ఎ.ఐ గురించి"},
    "login_success":{"English":"Logged in successfully!","Hindi":"सफलतापूर्वक लॉगिन किया गया!","Tamil":"வெற்றிகரமாக உள்நுழைந்தது!","Telugu":"విజయవంతంగా లాగిన్ అయ్యారు!"},
    "login_error":{"English":"Invalid username or password","Hindi":"अमान्य उपयोगकर्ता नाम या पासवर्ड","Tamil":"தவறான பயனர்பெயர் அல்லது கடவுச்சொல்","Telugu":"తప్పు వాడుకరి పేరు లేదా పాస్వర్డ్"},
    "sos_sent":{"English":"SOS Alert Sent!","Hindi":"SOS अलर्ट भेजा गया!","Tamil":"SOS எச்சரிக்கை அனுப்பப்பட்டது!","Telugu":"SOS హెచ్చరిక పంపబడింది!"}
}

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
        translations["login"][lang],
        translations["send_sos"][lang],
        "🤖 AI Prediction",
        "🌤 Weather Advisory",
        "💬 Community Updates",
        "📍 Real-time Location",
        "🗺️ Safe Zone Prediction",
        "🎤 Voice Assistant",
        "📈 Fishing Trends",
        "🗺️ Safe Routes",
        translations["alerts"][lang],
        translations["about"][lang]
    ]
)
st.sidebar.markdown("---")
st.sidebar.markdown("Made with ❤️ for Fishermen")

# --- Session State ---
if "user" not in st.session_state:
    st.session_state.user = None

# --- LOGIN ---
if menu == translations["login"][lang]:
    st.subheader(translations["login"][lang])
    username = st.text_input(translations["username"][lang])
    password = st.text_input(translations["password"][lang], type="password")
    if st.button(translations["login"][lang]):
        user_ref = db.collection("users").document(username).get()
        if user_ref.exists and user_ref.to_dict().get("password") == password:
            st.session_state.user = username
            st.success(translations["login_success"][lang])
        else:
            st.error(translations["login_error"][lang])

# --- SEND SOS ---
elif menu == translations["send_sos"][lang]:
    st.subheader(translations["send_sos"][lang])
    if st.session_state.user:
        msg = st.text_area("Message / संदेश / செய்தி / సందేశం")
        lat = st.text_input("Latitude (optional)")
        lon = st.text_input("Longitude (optional)")
        if st.button(translations["send_sos"][lang]):
            sos_id = str(uuid.uuid4())
            db.collection("sos_alerts").document(sos_id).set({
                "username": st.session_state.user,
                "message": msg,
                "latitude": lat,
                "longitude": lon,
                "timestamp": datetime.utcnow()
            })
            st.success(translations["sos_sent"][lang])
            speak(translations["sos_sent"][lang])
    else:
        st.warning("Please login to send SOS / लॉगिन करें / உள்நுழையவும் / లాగిన్ అవ్వండి")

# --- ALERTS ---
elif menu == translations["alerts"][lang]:
    st.subheader(translations["alerts"][lang])
    if st.session_state.user:
        sos_ref = db.collection("sos_alerts").order_by("timestamp", direction=firestore.Query.DESCENDING).limit(10)
        for doc in sos_ref.stream():
            d = doc.to_dict()
            st.info(f"{d.get('username','Unknown')} at ({d.get('latitude','N/A')}, {d.get('longitude','N/A')}): {d.get('message','No message')}")
    else:
        st.warning("Login to view alerts / लॉगिन करें / உள்நுழையவும் / లాగిన్ అవ్వండి")

# --- AI Prediction ---
elif menu == "🤖 AI Prediction":
    st.subheader("🤖 AI Fish Catch Prediction")
    st.markdown("Upload environmental JSON data (temperature, salinity, etc.)")
    uploaded_file = st.file_uploader("Upload JSON file")
    if uploaded_file:
        data = json.load(uploaded_file)
        # Dummy prediction logic (replace with your model)
        score = 0.7
        st.success(f"Predicted Fish Availability Score: {score*100:.1f}%")
        speak(f"Predicted Fish Availability Score {score*100:.1f} percent")

# --- Weather Advisory ---
elif menu == "🌤 Weather Advisory":
    st.subheader("🌤 Weather & Sea Advisory")
    lat = st.number_input("Latitude", value=8.5)
    lon = st.number_input("Longitude", value=78.1)
    st.info(f"Weather advisory for ({lat},{lon})")
    # Placeholder: replace with actual weather API if needed

# --- Community Updates ---
elif menu == "💬 Community Updates":
    st.subheader("💬 Community Updates")
    updates_ref = db.collection("community_updates").order_by("timestamp", direction=firestore.Query.DESCENDING).limit(5)
    for doc in updates_ref.stream():
        d = doc.to_dict()
        st.write(f"{d.get('username','Unknown')} : {d.get('message','No message')}")

# --- Real-time Location ---
elif menu == "📍 Real-time Location":
    st.subheader("📍 Real-time Location Tracker")
    if st.session_state.user:
        lat = st.number_input("Latitude", value=8.5, key="loc_lat")
        lon = st.number_input("Longitude", value=78.1, key="loc_lon")
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
        st.warning("Please login to update location")

# --- Safe Zone Prediction ---
elif menu == "🗺️ Safe Zone Prediction":
    st.subheader("🗺️ Safe Zone Prediction")
    # Dummy placeholder: replace with actual logic
    st.info("Safe zones based on recent SOS and weather data")

# --- Safe Routes ---
elif menu == "🗺️ Safe Routes":
    st.subheader("🗺️ Safe Routes Planner")
    # Dummy placeholder: replace with your route planning algorithm
    st.info("Safe routes between port and fishing zones")

# --- Fishing Trends ---
elif menu == "📈 Fishing Trends":
    st.subheader("📈 Fishing Trends")
    df = pd.DataFrame({
        "Day": ["Mon","Tue","Wed","Thu","Fri"],
        "Catch Score":[0.7,0.8,0.6,0.9,0.75]
    })
    st.line_chart(df.set_index("Day")["Catch Score"])

# --- Voice Assistant ---
elif menu == "🎤 Voice Assistant":
    st.subheader("🎤 Voice Assistant")
    command = get_browser_voice_command()
    if command:
        st.info(f"Command received: {command}")
        speak(f"You said: {command}")

# --- ABOUT ---
elif menu == translations["about"][lang]:
    st.subheader(translations["about"][lang])
    st_lottie(load_lottie_url("https://assets5.lottiefiles.com/packages/lf20_zrqthn6o.json"), height=200)
    st.markdown("""
    BlueWave AI is an advanced assistant platform for fishermen:
    - Send & receive SOS alerts
    - AI-based fish catch prediction
    - Real-time location tracking
    - Weather & sea condition advisories
    - Safe zone & route prediction
    - Community updates & trends
    - Voice assistant commands
    - Fully Cloud-compatible & mobile-friendly
    """)











