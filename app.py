
    # BlueWave AI - Fishermen Safety Assistant (Full Features)
import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore, auth
from google.cloud.firestore_v1.base_document import DocumentSnapshot

# Initialize Firebase
if "firebase_app" not in st.session_state:
    cred = credentials.Certificate(st.secrets["firebase"])
    firebase_admin.initialize_app(cred)
    st.session_state["firebase_app"] = True

db = firestore.client()

# Login Form
if "user" not in st.session_state:
    with st.form("login_form"):
        st.subheader("🔐 Login to BlueWave AI")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")

        if submit:
            try:
                user = auth.get_user_by_email(email)
                st.session_state["user"] = email
                st.success(f"Logged in as {email}")
                st.rerun()
            except Exception:
                st.error("Login failed. Please check your credentials.")
    st.stop()

st.sidebar.title("🌊 BlueWave AI Features")
feature = st.sidebar.radio("Choose a feature", [
    "Real-time GPS Tracking",
    "SOS Emergency Alert",
    "Fish Catch Prediction",
    "Fishing Zones Map",
    "Fish Catch Logging",
    "Voice Alerts",
    "Safe Route Planning",
    "Community Fish Zones",
    "Offline Mode",
    "Multilingual Support",
    "Push Notifications",
    "Emergency Contacts",
    "Leaderboard",
    "Badges & Rewards",
    "Recent SOS Alerts",
    "Live Firebase Alerts",
    "Heatmap Zones",
    "Fish Species Recognition",
    "Daily Tips"
])

st.title("BlueWave AI - Fishermen Safety Assistant")
st.subheader(f"🧭 {feature}")

# Sample Logic for Recent SOS Alerts Feature
if feature == "Recent SOS Alerts":
    st.info("Showing recent SOS alerts from fishermen")
    sos_ref = db.collection("sos_alerts")
    try:
        sos_docs = sos_ref.order_by("timestamp", direction=firestore.Query.DESCENDING).limit(10).stream()
        for a in sos_docs:
            a = a.to_dict() if isinstance(a, DocumentSnapshot) else a
            username = a.get("username", "Unknown")
            location = a.get("location")
            if location:
                st.write(f"🚨 {username} at {location.latitude},{location.longitude}")
            else:
                st.write(f"🚨 {username} (Location not available)")
    except Exception as e:
        st.error("Failed to fetch SOS alerts.")

# Placeholder for other features
elif feature == "Real-time GPS Tracking":
    st.map()  # placeholder
    st.success("Real-time GPS map will appear here.")

elif feature == "Fish Catch Prediction":
    st.success("AI fish catch prediction will be integrated here.")

elif feature == "Fishing Zones Map":
    st.success("Fishing zones overlay on map coming soon.")

elif feature == "Fish Catch Logging":
    st.success("Form to log fish catches.")

elif feature == "Voice Alerts":
    st.success("Voice alerts system will be integrated here.")

elif feature == "Safe Route Planning":
    st.success("Safe navigation route feature placeholder.")

elif feature == "Community Fish Zones":
    st.success("Community-submitted fishing zones.")

elif feature == "Offline Mode":
    st.success("App will support offline data capture.")

elif feature == "Multilingual Support":
    st.success("App supports English and Tamil.")

elif feature == "Push Notifications":
    st.success("Push notifications coming soon.")

elif feature == "Emergency Contacts":
    st.success("Add and manage emergency contacts.")

elif feature == "Leaderboard":
    st.success("Fishing leaderboard by catch volume.")

elif feature == "Badges & Rewards":
    st.success("Gamification with badges and rewards.")

elif feature == "Live Firebase Alerts":
    st.success("Live alerts from Firebase will appear here.")

elif feature == "Heatmap Zones":
    st.success("Heatmap of fishing activity.")

elif feature == "Fish Species Recognition":
    st.success("Upload fish photo for species detection.")

elif feature == "Daily Tips":
    st.success("Fishing safety and tips for the day.")
