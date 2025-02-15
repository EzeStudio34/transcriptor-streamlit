import requests
import streamlit as st

# URL del Google Apps Script Web App (Reemplázala con tu URL real)
script_url = "https://script.google.com/macros/s/https://script.google.com/macros/s/AKfycbwc8VLPe0L3xk7lPbbjKyOoQ-a5SOT8-jeuVTk32UJkr72m7rEX9hE7okuAsxe88lLr1w/exec/exec"

st.title("🔄 Prueba de Conexión con Google Apps Script")

# Datos de prueba
data = {
    "texto": "Esta es una prueba de transcripción desde Streamlit.",
    "duracion": "60",
    "tematica": "Educación"
}

st.write("📤 Enviando solicitud a Google Apps Script...")

# Enviar datos a Google Apps Script
response = requests.post(script_url, json=data)

# Mostrar la respuesta de la API en Streamlit
st.write(f"📤 Respuesta de Google Apps Script: {response.text}")
