import streamlit as st
import os
from google import genai
from google.genai import types

from services.tts_service import text_to_speech
from components.avatar_widget import render_interactive_avatar

st.set_page_config(
    page_title="RoboMANTAP — AI Assistant",
    page_icon="🤖",
    layout="centered"
)

# Header Platform
st.markdown("<h2 style='text-align: center; color: #047857;'>🤖 RoboMANTAP — AI Assistant</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #6B7280;'>Platform Pembelajaran Pintar Al-Irsyad Al-Islamiyah</p>", unsafe_allow_html=True)

# 1. Inisialisasi Client Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")  # Isi API Key jika di-hardcode
client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

CHARACTER_IMAGE = os.path.join("components", "character.png")
AUDIO_RESPONSE_PATH = "temp_response.mp3"

if "last_audio" not in st.session_state:
    st.session_state.last_audio = None

# 2. Tangkap Suara dari Query Parameter (Dikirim dari JS Widget)
voice_input = st.query_params.get("speech_text", "")

# 3. Proses Otomatis Jika Ada Input Suara
if voice_input:
    # Bersihkan parameter URL
    st.query_params.clear()
    
    with st.spinner("🤖 RoboMANTAP sedang berpikir dan menyusun jawaban..."):
        # A. Tanya ke Gemini AI
        if client:
            try:
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=voice_input,
                    config=types.GenerateContentConfig(
                        system_instruction=(
                            "Jawablah sebagai RoboMANTAP, asisten pembelajaran pintar Al-Irsyad "
                            "yang ramah, ringkas, ceria, dan mudah dipahami oleh siswa. "
                            "Gunakan bahasa lisan yang natural untuk diucapkan."
                        ),
                        temperature=0.7,
                    )
                )
                ai_reply = response.text
            except Exception as e:
                ai_reply = f"Maaf, ada kendala koneksi: {str(e)}"
        else:
            ai_reply = f"Halo! Terima kasih sudah bertanya tentang {voice_input}. Mari kita pelajari materi ini bersama-sama di kelas!"

        # B. Ubah Jawaban Teks Menjadi Audio Suara (.mp3)
        text_to_speech(ai_reply, output_file=AUDIO_RESPONSE_PATH)
        
        # C. Simpan Audio ke Session State & Reload Halaman
        st.session_state.last_audio = AUDIO_RESPONSE_PATH
        st.rerun()

# 4. Render Widget Avatar Interaktif (Satu-satunya Tampilan Utama)
render_interactive_avatar(CHARACTER_IMAGE, audio_path=st.session_state.last_audio)

# Tampilkan Teks Transkrip Terakhir (Opsional untuk Aksesibilitas)
if voice_input:
    st.success(f"🗣️ **Anda:** {voice_input}")