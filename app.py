# BlueWave AI - Fishermen Safety Assistant (No Login + Full Voice + Folium Maps)
import streamlit as st
from firebase_admin import credentials, firestore, initialize_app
import firebase_admin
from datetime import datetime, timedelta
import uuid
import json
import pandas as pd
import folium
from streamlit_folium import st_folium

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
        "English":"🌊 BlueWave AI - Fishermen Safety Assistant",
        "Hindi":"🌊 ब्लूवेव एआई - मछुआरों के लिए सुरक्षा सहायक",
        "Tamil":"🌊 புளூவேவ் ஏ.ஐ - மீனவர்களின் பாதுகாப்பு உதவி",
        "Telugu":"🌊 బ్లూవేవ్ ఎ.ఐ - మత్స్యకారుల భద్రతా సహాయకుడు"
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
    "fishing_trends": {
        "English":"Fishing Trends",
        "Hindi":"मछली पकड़ने के रुझान",
        "Tamil":"மீன் பிடிக்கும் போக்குகள்",
        "Telugu":"చేప పట్టు ధోరణులు"
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
    "sos_sent": {
        "English":"SOS Alert Sent!",
        "Hindi":"SOS अलर्ट भेजा गया!",
        "Tamil":"SOS எச்சரிக்கை அனுப்பப்பட்டது!",
        "Telugu":"SOS హెచ్చరిక పంపబడింది!"
    }
}

# --- Firebase Setup ---
if not firebase_admin._apps:
    cred = credentials.Certificate(dict(st.secrets["firebase"]))
    initialize_app(cred)
db = firestore.client()

# --- Browser TTS ---
def speak(text):
    st.components.v1.html(f"""
        <script>
            var msg = new SpeechSynthesisUtterance("{text}");
            window.speechSynthesis.speak(msg);
        </script>
        """, height=0)

# --- Sidebar Navigation ---
menu = st.sidebar.radio(
    translations["title"][lang],
    [
        translations["send_sos"][lang],
        translations["ai_prediction"][lang],
        translations["weather_advisory"][lang],
        translations["community_updates"][lang],
        "📍 Real-time Location",
        translations["safe_zone_prediction"][lang],
        translations["voice_assistant"][lang],
        translations["fishing_trends"][lang],
        translations["safe_routes"][lang],
        translations["alerts"][lang],
        translations["title"][lang]  # About
    ]
)
st.sidebar.markdown("---")
st.sidebar.markdown("Made with ❤️ for Fishermen")

# --- SEND SOS ---
if menu == translations["send_sos"][lang]:
    st.subheader(translations["send_sos"][lang])
    msg = st.text_area(translations["sos_message"][lang])
    lat = st.text_input(translations["latitude"][lang])
    lon = st.text_input(translations["longitude"][lang])
    if st.button(translations["send_sos"][lang]):
        sos_id = str(uuid.uuid4())
        db.collection("sos_alerts").document(sos_id).set({
            "username": "Anonymous",
            "message": msg,
            "latitude": lat,
            "longitude": lon,
            "timestamp": datetime.utcnow()
        })
        st.success(translations["sos_sent"][lang])
        speak(translations["sos_sent"][lang])

# --- ALERTS ---
elif menu == "📢 Nearby Alerts":
    st.subheader(translations["alerts"][lang])
    sos_ref = db.collection("sos_alerts").order_by("timestamp", direction=firestore.Query.DESCENDING).limit(10)
    alerts_text = ""
    for doc in sos_ref.stream():
        d = doc.to_dict()
        alerts_text += f"{d.get('username','Unknown')} at ({d.get('latitude','N/A')},{d.get('longitude','N/A')}): {d.get('message','No message')}\n"
        st.info(f"{d.get('username','Unknown')} at ({d.get('latitude','N/A')},{d.get('longitude','N/A')}): {d.get('message','No message')}")
    if alerts_text:
        speak(alerts_text)

# --- AI Prediction ---
elif menu == translations["ai_prediction"][lang]:
    st.subheader(translations["ai_prediction"][lang])
    uploaded_file = st.file_uploader(translations["upload_json"][lang])
    if uploaded_file:
        try:
            data = json.load(uploaded_file)
            score = 0.7
            st.success(f"Predicted Fish Availability Score: {score*100:.1f}%")
            speak(f"Predicted Fish Availability Score {score*100:.1f} percent")
        except Exception as e:
            st.error("Invalid JSON file. Please upload a correct JSON.")
            speak("Invalid JSON file. Please upload a correct JSON.")

# --- Real-time Location ---
elif menu == "📍 Real-time Location":
    st.subheader("📍 Real-time Location Tracker")
    lat = st.number_input(translations["latitude"][lang], value=8.5, key="loc_lat")
    lon = st.number_input(translations["longitude"][lang], value=78.1, key="loc_lon")
    if st.button(translations["update_location"][lang]):
        db.collection("locations").document("Anonymous").set({
            "username": "Anonymous",
            "latitude": lat,
            "longitude": lon,
            "timestamp": datetime.utcnow()
        })
        st.success(translations["location_updated"][lang])
        speak(translations["location_updated"][lang])
    m = folium.Map(location=[lat, lon], zoom_start=10)
    folium.Marker([lat, lon], tooltip="You are here").add_to(m)
    st_folium(m, width=700, height=500)

# --- Safe Zone Prediction ---
elif menu == translations["safe_zone_prediction"][lang]:
    st.subheader(translations["safe_zone_prediction"][lang])
    recent_sos = db.collection("sos_alerts").where(
        "timestamp", ">=", datetime.utcnow() - timedelta(hours=24)
    ).stream()
    danger_points = []
    for doc in recent_sos:
        d = doc.to_dict()
        try:
            danger_points.append([float(d.get("latitude",0)), float(d.get("longitude",0))])
        except:
            continue
    m_zone = folium.Map(location=[8.5,78.1], zoom_start=10)
    grid_points = [[(8.6,78.0),(8.6,78.2),(8.4,78.2),(8.4,78.0)]]
    for zone in grid_points:
        in_danger = any(zone[2][0] <= p[0] <= zone[0][0] and zone[0][1] <= p[1] <= zone[1][1] for p in danger_points)
        color = "red" if in_danger else "green"
        folium.Polygon(locations=zone, color=color, fill=True, fill_opacity=0.4, tooltip="Safe Zone" if color=="green" else "Danger Zone").add_to(m_zone)
    st_folium(m_zone, width=700, height=500)
    speak("Safe zone prediction updated")

# --- Safe Routes ---
elif menu == translations["safe_routes"][lang]:
    st.subheader(translations["safe_routes"][lang])
    port = [8.5, 78.0]
    recent_sos = db.collection("sos_alerts").where(
        "timestamp", ">=", datetime.utcnow() - timedelta(hours=24)
    ).stream()
    danger_points = []
    for doc in recent_sos:
        d = doc.to_dict()
        try:
            danger_points.append([float(d.get("latitude",0)), float(d.get("longitude",0))])
        except:
            continue
    safe_fishing = [8.6,78.1]
    m_route = folium.Map(location=port, zoom_start=11)
    folium.Marker(port, tooltip="Port", icon=folium.Icon(color="blue")).add_to(m_route)
    folium.Marker(safe_fishing, tooltip="Safe Fishing Zone", icon=folium.Icon(color="green")).add_to(m_route)
    folium.PolyLine([port, safe_fishing], color="green", weight=5, tooltip="Safe Route").add_to(m_route)
    for p in danger_points:
        folium.CircleMarker(location=p, radius=5, color="red", fill=True, fill_opacity=0.7, tooltip="Danger Zone").add_to(m_route)
    st_folium(m_route, width=700, height=500)
    speak("Safe route updated")

# --- Fishing Trends ---
elif menu == translations["fishing_trends"][lang]:
    st.subheader(translations["fishing_trends"][lang])
    df = pd.DataFrame({"Day":["Mon","Tue","Wed","Thu","Fri"],"Catch Score":[0.7,0.8,0.6,0.9,0.75]})
    st.line_chart(df.set_index("Day")["Catch Score"])
    speak("Displaying fishing trends for the week")

# --- Voice Assistant ---
elif menu == translations["voice_assistant"][lang]:
    st.subheader(translations["voice_assistant"][lang])
    st.info("🎤 Enter your command here (simulate voice input)")
    command = st.text_input("Type your command here")
    if st.button("Speak Command") and command:
        st.info(f"Command received: {command}")
        speak(f"You said: {command}")

# --- Weather Advisory ---
elif menu == translations["weather_advisory"][lang]:
    st.subheader(translations["weather_advisory"][lang])
    lat = st.number_input(translations["latitude"][lang], value=8.5)
    lon = st.number_input(translations["longitude"][lang], value=78.1)
    st.info(f"Weather advisory for ({lat},{lon})")
    speak(f"Weather advisory for latitude {lat} and longitude {lon}")

# --- Community Updates ---
elif menu == translations["community_updates"][lang]:
    st.subheader(translations["community_updates"][lang])
    updates_ref = db.collection("community_updates").order_by("timestamp", direction=firestore.Query.DESCENDING).limit(5)
    updates_text = ""
    for doc in updates_ref.stream():
        d = doc.to_dict()
        updates_text += f"{d.get('username','Unknown')} : {d.get('message','No message')}. "
        st.write(f"{d.get('username','Unknown')} : {d.get('message','No message')}")
    if updates_text:
        speak(updates_text)

# --- ABOUT ---
elif menu == translations["About"][lang]:
    st.subheader(translations["About"][lang])
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

