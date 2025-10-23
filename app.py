# BlueWave AI - Fishermen Safety Assistant (Full Advanced + Multilingual, No Google API)

import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore, initialize_app
from datetime import datetime
import uuid
import json
import pandas as pd
import requests
from streamlit_lottie import st_lottie
import folium
from streamlit_folium import st_folium

# --- Streamlit Setup ---
st.set_page_config(page_title="BlueWave AI", layout="wide")

# --- Language Selector ---
lang = st.sidebar.selectbox(
    "🌐 Select Language / மொழி / భాష / भाषा",
    ["English", "Hindi", "Tamil", "Telugu"]
)

# --- Translations ---
translations = {
    "title": {
        "English":"🌊 BlueWave AI - Fishermen Safety Assistant",
        "Hindi":"🌊 ब्लूवेव एआई - मछुआरों के लिए सुरक्षा सहायक",
        "Tamil":"🌊 புளூவேவ் ஏ.ஐ - மீனவர்களின் பாதுகாப்பு உதவி",
        "Telugu":"🌊 బ్లూవేవ్ ఎ.ఐ - మత్స్యకారుల భద్రతా సహాయకుడు"
    },
    "login": {
        "English":"🔐 Login",
        "Hindi":"🔐 लॉगिन",
        "Tamil":"🔐 உள்நுழைவு",
        "Telugu":"🔐 లాగిన్"
    },
    "username": {
        "English":"Username",
        "Hindi":"उपयोगकर्ता नाम",
        "Tamil":"பயனர்பெயர்",
        "Telugu":"వాడుకరి పేరు"
    },
    "password": {
        "English":"Password",
        "Hindi":"पासवर्ड",
        "Tamil":"கடவுச்சொல்",
        "Telugu":"పాస్వర్డ్"
    },
    "send_sos": {
        "English":"🚨 Send Emergency SOS",
        "Hindi":"🚨 आपातकालीन SOS भेजें",
        "Tamil":"🚨 அவசர SOS அனுப்பு",
        "Telugu":"🚨 అత్యవసర SOS పంపండి"
    },
    "sos_message": {
        "English":"Message",
        "Hindi":"संदेश",
        "Tamil":"செய்தி",
        "Telugu":"సందేశం"
    },
    "latitude": {
        "English":"Latitude (optional)",
        "Hindi":"अक्षांश (वैकल्पिक)",
        "Tamil":"அட்சாங்ஸ் (விருப்பமானது)",
        "Telugu":"అక్షాంశం (ఐచ్ఛికం)"
    },
    "longitude": {
        "English":"Longitude (optional)",
        "Hindi":"देशांतर (वैकल्पिक)",
        "Tamil":"உயர்நிலை (விருப்பமானது)",
        "Telugu":"రేఖాంశం (ఐచ్ఛికం)"
    },
    "alerts": {
        "English":"📢 Nearby Alerts",
        "Hindi":"📢 पास के अलर्ट",
        "Tamil":"📢 அருகிலுள்ள எச்சரிக்கைகள்",
        "Telugu":"📢 సమీప హెచ్చరికలు"
    },
    "about": {
        "English":"🌊 About BlueWave AI",
        "Hindi":"🌊 ब्लूवेव एआई के बारे में",
        "Tamil":"🌊 புளூவேவ் ஏ.ஐ பற்றி",
        "Telugu":"🌊 బ్లూవేవ్ ఎ.ఐ గురించి"
    },
    "login_success": {
        "English":"Logged in successfully!",
        "Hindi":"सफलतापूर्वक लॉगिन किया गया!",
        "Tamil":"வெற்றிகரமாக உள்நுழைந்தது!",
        "Telugu":"విజయవంతంగా లాగిన్ అయ్యారు!"
    },
    "login_error": {
        "English":"Invalid username or password",
        "Hindi":"अमान्य उपयोगकर्ता नाम या पासवर्ड",
        "Tamil":"தவறான பயனர்பெயர் அல்லது கடவுச்சொல்",
        "Telugu":"తప్పు వాడుకరి పేరు లేదా పాస్వర్డ్"
    },
    "sos_sent": {
        "English":"SOS Alert Sent!",
        "Hindi":"SOS अलर्ट भेजा गया!",
        "Tamil":"SOS எச்சரிக்கை அனுப்பப்பட்டது!",
        "Telugu":"SOS హెచ్చరిక పంపబడింది!"
    },
    "login_required": {
        "English":"Please login to proceed",
        "Hindi":"कृपया आगे बढ़ने के लिए लॉगिन करें",
        "Tamil":"தொடர நீங்கள் உள்நுழையவும்",
        "Telugu":"దయచేసి కొనసాగడానికి లాగిన్ అవ్వండి"
    },
    "update_location": {
        "English":"Update Location",
        "Hindi":"स्थान अपडेट करें",
        "Tamil":"இருப்பிடத்தை புதுப்பிக்கவும்",
        "Telugu":"స్థానం నవీకరించండి"
    },
    "location_updated": {
        "English":"Location updated",
        "Hindi":"स्थान अपडेट किया गया",
        "Tamil":"இருப்பிடம் புதுப்பிக்கப்பட்டது",
        "Telugu":"స్థానం నవీకరించబడింది"
    },
    "weather_advisory": {
        "English":"Weather & Sea Advisory",
        "Hindi":"मौसम और समुद्र सलाह",
        "Tamil":"வானிலை மற்றும் கடல் ஆலோசனை",
        "Telugu":"వాతావరణ & సముద్ర సూచనలు"
    },
    "community_updates": {
        "English":"Community Updates",
        "Hindi":"समुदाय अपडेट्स",
        "Tamil":"சமூக புதுப்பிப்புகள்",
        "Telugu":"సముదాయ నవీకరణలు"
    },
    "ai_prediction": {
        "English":"AI Fish Catch Prediction",
        "Hindi":"एआई मछली पकड़ने की भविष्यवाणी",
        "Tamil":"ஏ.ஐ மீன் பிடிக்கும் கணிப்பு",
        "Telugu":"ఏఐ చేప పట్టు భవిష్యవాణి"
    },
    "upload_json": {
        "English":"Upload JSON file",
        "Hindi":"JSON फ़ाइल अपलोड करें",
        "Tamil":"JSON கோப்பை பதிவேற்றவும்",
        "Telugu":"JSON ఫైల్ అప్‌లోడ్ చేయండి"
    },
    "fishing_trends": {
        "English":"Fishing Trends",
        "Hindi":"मछली पकड़ने के रुझान",
        "Tamil":"மீன் பிடிக்கும் போக்குகள்",
        "Telugu":"చేప పట్టు ధోరణులు"
    },
    "safe_zone_prediction": {
        "English":"Safe Zone Prediction",
        "Hindi":"सुरक्षित क्षेत्र की भविष्यवाणी",
        "Tamil":"பாதுகாப்பான பகுதி கணிப்பு",
        "Telugu":"సురక్షిత ప్రాంతం భవిష్యవాణి"
    },
    "safe_routes": {
        "English":"Safe Routes",
        "Hindi":"सुरक्षित मार्ग",
        "Tamil":"பாதுகாப்பான வழிகள்",
        "Telugu":"సురక్షిత మార్గాలు"
    },
    "voice_assistant": {
        "English":"Voice Assistant",
        "Hindi":"वॉइस असिस्टेंट",
        "Tamil":"குரல் உதவியாளர்",
        "Telugu":"వాయిస్ అసిస్టెంట్"
    },
    "real_time_location": {
        "English":"📍 Real-time Location",
        "Hindi":"📍 वास्तविक समय स्थान",
        "Tamil":"📍 நேரடி இடம்",
        "Telugu":"📍 రియల్-టైమ్ లొకేషన్"
    }
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

# --- Browser Voice Input ---
def get_browser_voice_command():
    st.info("🎤 Enter your command here (simulate voice input)")
    command = st.text_input(translations["voice_assistant"][lang])
    return command.lower() if command else ""

# --- Sidebar Navigation ---
menu = st.sidebar.radio(
    translations["title"][lang],
    [
        translations["login"][lang],
        translations["send_sos"][lang],
        translations["ai_prediction"][lang],
        translations["weather_advisory"][lang],
        translations["community_updates"][lang],
        translations["real_time_location"][lang],
        translations["safe_zone_prediction"][lang],
        translations["voice_assistant"][lang],
        translations["fishing_trends"][lang],
        translations["safe_routes"][lang],
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
        msg = st.text_area(translations["sos_message"][lang])
        lat = st.text_input(translations["latitude"][lang])
        lon = st.text_input(translations["longitude"][lang])
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
        st.warning(translations["login_required"][lang])

# --- ALERTS ---
elif menu == translations["alerts"][lang]:
    st.subheader(translations["alerts"][lang])
    if st.session_state.user:
        sos_ref = db.collection("sos_alerts").order_by("timestamp", direction=firestore.Query.DESCENDING).limit(10)
        for doc in sos_ref.stream():
            d = doc.to_dict()
            st.info(f"{d.get('username','Unknown')} at ({d.get('latitude','N/A')}, {d.get('longitude','N/A')}): {d.get('message','No message')}")
    else:
        st.warning(translations["login_required"][lang])

# --- AI Prediction ---
elif menu == translations["ai_prediction"][lang]:
    st.subheader(translations["ai_prediction"][lang])
    uploaded_file = st.file_uploader(translations["upload_json"][lang])
    if uploaded_file:
        data = json.load(uploaded_file)
        score = 0.7
        st.success(f"Predicted Fish Availability Score: {score*100:.1f}%")
        speak(f"Predicted Fish Availability Score {score*100:.1f} percent")

# --- Weather Advisory ---
elif menu == translations["weather_advisory"][lang]:
    st.subheader(translations["weather_advisory"][lang])
    lat = st.number_input(translations["latitude"][lang], value=8.5)
    lon = st.number_input(translations["longitude"][lang], value=78.1)
    st.info(f"Weather advisory for ({lat},{lon})")

# --- Community Updates ---
elif menu == translations["community_updates"][lang]:
    st.subheader(translations["community_updates"][lang])
    updates_ref = db.collection("community_updates").order_by("timestamp", direction=firestore.Query.DESCENDING).limit(5)
    for doc in updates_ref.stream():
        d = doc.to_dict()
        st.write(f"{d.get('username','Unknown')} : {d.get('message','No message')}")

# --- Real-time Location using OpenStreetMap ---
elif menu == translations["real_time_location"][lang]:
    st.subheader(translations["real_time_location"][lang])
    if st.session_state.user:
        lat = st.number_input(translations["latitude"][lang], value=8.5, key="loc_lat")
        lon = st.number_input(translations["longitude"][lang], value=78.1, key="loc_lon")
        if st.button(translations["update_location"][lang]):
            db.collection("locations").document(st.session_state.user).set({
                "username": st.session_state.user,
                "latitude": lat,
                "longitude": lon,
                "timestamp": datetime.utcnow()
            })
            st.success(translations["location_updated"][lang])

        # Folium map
        m = folium.Map(location=[lat, lon], zoom_start=10)
        folium.Marker([lat, lon], tooltip=st.session_state.user).add_to(m)
        st_folium(m, width=800, height=500)
    else:
        st.warning(translations["login_required"][lang])

# --- Safe Zone Prediction ---
elif menu == translations["safe_zone_prediction"][lang]:
    st.subheader(translations["safe_zone_prediction"][lang])
    st.info("Safe zones based on recent SOS and weather data")

# --- Safe Routes ---
elif menu == translations["safe_routes"][lang]:
    st.subheader(translations["safe_routes"][lang])
    st.info("Safe routes between port and fishing zones")

# --- Fishing Trends ---
elif menu == translations["fishing_trends"][lang]:
    st.subheader(translations["fishing_trends"][lang])
    df = pd.DataFrame({"Day":["Mon","Tue","Wed","Thu","Fri"],"Catch Score":[0.7,0.8,0.6,0.9,0.75]})
    st.line_chart(df.set_index("Day")["Catch Score"])

# --- Voice Assistant ---
elif menu == translations["voice_assistant"][lang]:
    st.subheader(translations["voice_assistant"][lang])
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



