import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import time

# --- Page Configuration ---
st.set_page_config(page_title="BlueWave AI - Fishermen Safety Assistant", layout="wide")

# --- Firebase Initialization ---
if not firebase_admin._apps:
    cred = credentials.Certificate(st.secrets["firebase"])
    firebase_admin.initialize_app(cred)

db = firestore.client()

# --- Session State Initialization ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

# --- Login Form ---
def login():
    st.title("🔐 BlueWave AI - Login")
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")

        if submit:
            user_ref = db.collection("users").document(username)
            user_doc = user_ref.get()

            if user_doc.exists:
                user_data = user_doc.to_dict()
                if user_data.get("password") == password:
                    st.success("Login successful!")
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    time.sleep(1)
                    st.experimental_rerun()
                else:
                    st.error("Incorrect password.")
            else:
                st.error("User not found.")

# --- Main App Interface ---
def main_app():
    st.sidebar.title(f"👤 Welcome, {st.session_state.username}")
    option = st.sidebar.radio("Choose Feature", ["🏠 Dashboard", "📍 Live Map", "🚨 SOS", "📦 Log Out"])

    if option == "🏠 Dashboard":
        st.title("🌊 BlueWave AI - Fishermen Safety Assistant")
        st.markdown("Welcome to the safety assistant dashboard.")
    elif option == "📍 Live Map":
        st.title("📍 Real-Time Map")
        st.components.v1.html(
            f"""
            <iframe
                width="100%"
                height="500"
                style="border:0"
                loading="lazy"
                allowfullscreen
                referrerpolicy="no-referrer-when-downgrade"
                src="https://www.google.com/maps/embed/v1/view?key={st.secrets['GOOGLE_MAPS_API_KEY']}&center=10.7905,78.7047&zoom=7">
            </iframe>
            """,
            height=500,
        )
    elif option == "🚨 SOS":
        st.title("🚨 SOS Emergency")
        if st.button("Send SOS"):
            db.collection("sos").add({
                "username": st.session_state.username,
                "timestamp": firestore.SERVER_TIMESTAMP
            })
            st.success("🚨 SOS alert sent!")
    elif option == "📦 Log Out":
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.experimental_rerun()

# --- App Logic ---
if st.session_state.logged_in:
    main_app()
else:
    login()
