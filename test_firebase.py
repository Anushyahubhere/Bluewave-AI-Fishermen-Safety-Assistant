import streamlit as st
import firebase_admin
from firebase_admin import credentials

# Load Firebase credentials from st.secrets
try:
    cred = credentials.Certificate(st.secrets["firebase"])
    firebase_admin.initialize_app(cred)
    st.write("✅ Firebase credentials loaded successfully.")
except Exception as e:
    st.write("❌ Error loading Firebase credentials:", e)


