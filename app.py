
    # BlueWave AI - Fishermen Safety Assistant (Full Features)
import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore

# Set page config
st.set_page_config(page_title="BlueWave AI - Fishermen Safety Assistant", layout="wide")

# Initialize Firebase only once
if not firebase_admin._apps:
    cred = credentials.Certificate(st.secrets["firebase"])
    firebase_admin.initialize_app(cred)

# Firestore DB
db = firestore.client()



# Session state 



# -------------------- LANG --------------------
lang = st.sidebar.radio("🌐 Language / மொழி", ["English", "தமிழ்"])
T = lambda e, t: e if lang == "English" else t

# -------------------- LOGIN --------------------
st.title("🌊 BlueWave AI - Fishermen Safety Assistant")
st.subheader(T("Login", "உள் நுழை"))

username = st.text_input(T("Username", "பயனர் பெயர்"))
password = st.text_input(T("Password", "கடவுச்சொல்"), type="password")
login_btn = st.button(T("Login", "உள்நுழைய"))

user_doc = None
if login_btn:
    users_ref = db.collection("users")
    query = users_ref.where("username", "==", username).where("password", "==", password).stream()
    user_doc = next(query, None)
    if user_doc:
        st.success(T("Login successful ✅", "உள் நுழைவு வெற்றிகரமாக முடிந்தது ✅"))
        st.session_state["logged_in"] = True
        st.session_state["user"] = user_doc.to_dict()
    else:
        st.error(T("Invalid credentials ❌", "தவறான பயனர் விவரங்கள் ❌"))

# -------------------- MAIN UI --------------------
if st.session_state.get("logged_in"):

    st.markdown("## 🧭 Features")
    feature = st.selectbox(
        T("Choose a feature", "ஒரு அம்சத்தைத் தேர்ந்தெடுக்கவும்"),
        [
            T("Send SOS Alert", "அவசர எச்சரிக்கை அனுப்பு"),
            T("View Live Map", "தற்போதைய வரைபடம்"),
            T("View Fish Zones", "மீன் பகுதிகளைப் பார்க்க"),
            T("Safe Route Planning", "பாதுகாப்பான பாதை திட்டமிடல்"),
            T("Catch Logbook", "மீன் பிடிப்பு பதிவேடு"),
            T("Leaderboard", "முன்னணி பட்டியல்"),
            T("Settings", "அமைப்புகள்")
        ]
    )

    # 1. SOS Alert
    if feature.startswith("Send SOS") or feature.startswith("அவசர"):
        st.warning(T("⚠️ Send emergency alert with current GPS.", "⚠️ தற்போதைய இடத்துடன் அவசர எச்சரிக்கை அனுப்பவும்"))
        lat = st.number_input("Latitude", format="%.6f")
        lon = st.number_input("Longitude", format="%.6f")
        sos_btn = st.button("📡 Send SOS")
        if sos_btn:
            db.collection("sos").add({
                "username": username,
                "location": firestore.GeoPoint(lat, lon),
                "timestamp": datetime.utcnow(),
                "id": str(uuid.uuid4())
            })
            st.success(T("🚨 SOS Sent!", "🚨 அவசர எச்சரிக்கை அனுப்பப்பட்டது!"))

    # 2. Live Map
    elif feature.startswith("View Live Map") or feature.startswith("தற்போதைய"):
        st.info("🌍 " + T("Live SOS locations map", "நேரடி SOS இடங்கள் வரைபடம்"))
        sos_docs = db.collection("sos").stream()
        for doc in sos_docs:
            data = doc.to_dict()
            try:
                lat, lon = data["location"].latitude, data["location"].longitude
                st.write(f"📍 {data['username']} at ({lat}, {lon})")
                st.map([{"lat": lat, "lon": lon}])
            except Exception as e:
                st.warning(f"Skipped a faulty location: {e}")

    # 3. Fish Zones (mocked overlay)
    elif feature.startswith("View Fish Zones") or feature.startswith("மீன்"):
        st.success(T("🗺️ Fish Catch Zones Overlaid", "🗺️ மீன் பிடிப்பு பகுதிகள் காட்டப்பட்டுள்ளன"))
        st.image("https://i.imgur.com/FishZones.png", caption="Fish Zone Overlay (Example)", use_column_width=True)

    # 4. Route Planning
    elif feature.startswith("Safe Route") or feature.startswith("பாதுகாப்பான"):
        st.info("🧭 " + T("Plan your safe return path.", "பாதுகாப்பான திரும்பும் பாதையை திட்டமிடுங்கள்."))
        st.text_input("Start Location")
        st.text_input("Destination")
        st.button("🚤 Plot Route")

    # 5. Logbook
    elif feature.startswith("Catch Logbook") or feature.startswith("பிடிப்பு"):
        st.text_input("Fish Type")
        st.number_input("Weight (kg)", min_value=0.0)
        st.date_input("Catch Date")
        st.button("📝 Log Catch")

    # 6. Leaderboard
    elif feature.startswith("Leaderboard") or feature.startswith("முன்னணி"):
        st.balloons()
        st.write("🏆 Leaderboard coming soon!")

    # 7. Settings
    elif feature.startswith("Settings") or feature.startswith("அமைப்புகள்"):
        st.toggle("Enable Notifications")
        st.toggle("Dark Mode")
        st.selectbox("Language", ["English", "தமிழ்"])

# -------------------- END --------------------
st.markdown("---")
st.caption("Built with ❤️ for Fishermen - BlueWave AI")
