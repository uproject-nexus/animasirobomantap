import os
import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types

from services.tts_service import text_to_speech
from components.avatar_widget import render_interactive_avatar

load_dotenv()

# ------------------------------------------------------------------------------
# 1. KONFIGURASI HALAMAN & MODEL
# ------------------------------------------------------------------------------
st.set_page_config(
    page_title="RoboMANTAP — AI Assistant",
    page_icon="🤖",
    layout="centered"
)

st.markdown("<h2 style='text-align: center; color: #047857;'>🤖 RoboMANTAP — AI Assistant</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #6B7280;'>Platform Pembelajaran Pintar Al-Irsyad Al-Islamiyah</p>", unsafe_allow_html=True)

# Model khusus interaksi LIVE: prioritaskan latency paling rendah
STREAM_MODELS = ("gemini-3.5-flash-lite", "gemini-3.1-flash-lite")
STREAM_TIMEOUT_MS = 90_000
AUDIO_RESPONSE_PATH = "temp_response.mp3"
CHARACTER_IMAGE = os.path.join("components", "character.png")

# ------------------------------------------------------------------------------
# 2. SELECTION & CACHING API KEYS / CLIENTS
# ------------------------------------------------------------------------------
def get_api_keys() -> list[str]:
    """Mengambil daftar API keys dari Streamlit secrets atau environment variables."""
    api_keys = []
    
    if "GEMINI_API_KEYS" in st.secrets:
        raw_keys = st.secrets["GEMINI_API_KEYS"]
        if isinstance(raw_keys, (list, tuple)):
            api_keys = list(raw_keys)
        elif isinstance(raw_keys, str):
            api_keys = [k.strip() for k in raw_keys.split(",") if k.strip()]
    elif os.getenv("GEMINI_API_KEY"):
        api_keys = [os.getenv("GEMINI_API_KEY")]

    return api_keys

@st.cache_resource(show_spinner=False)
def get_gemini_clients() -> list[genai.Client]:
    """Reuse koneksi Gemini antar rerun Streamlit."""
    keys = get_api_keys()
    clients = []

    for key in keys:
        try:
            client = genai.Client(
                api_key=key,
                http_options=types.HttpOptions(
                    timeout=STREAM_TIMEOUT_MS,
                    retry_options=types.HttpRetryOptions(attempts=1),
                ),
            )
            clients.append(client)
        except Exception:
            continue

    return clients

def _stream_config(model_name: str) -> types.GenerateContentConfig:
    """Konfigurasi live untuk meminimalkan latency."""
    system_instruction = (
        "Jawablah sebagai RoboMANTAP, asisten pembelajaran pintar Al-Irsyad "
        "yang ramah, ringkas, ceria, dan sangat mudah dipahami siswa. "
        "Gunakan bahasa lisan yang natural untuk diucapkan."
    )
    
    try:
        return types.GenerateContentConfig(
            system_instruction=system_instruction,
            max_output_tokens=1000,
            thinking_config=types.ThinkingConfig(
                thinking_budget=0,  # Berpikir 0 detik agar respon instan
                include_thoughts=False,
            ),
        )
    except Exception:
        return types.GenerateContentConfig(
            system_instruction=system_instruction,
            max_output_tokens=1000
        )

# ------------------------------------------------------------------------------
# 3. ESEKUSI JAWABAN DENGAN ROTASI KEY & MODEL FALLBACK
# ------------------------------------------------------------------------------
def generate_response_with_rotation(prompt: str) -> str:
    """Memutar penggunaan API Key (Round-Robin) & Fallback Model."""
    clients = get_gemini_clients()
    
    if not clients:
        return f"Halo! Terima kasih sudah bertanya tentang '{prompt}'. Mari kita pelajari materi ini bersama-sama di kelas!"

    num_clients = len(clients)
    if "key_index" not in st.session_state:
        st.session_state.key_index = 0

    last_exception = None

    for model_name in STREAM_MODELS:
        config = _stream_config(model_name)

        for attempt in range(num_clients):
            current_idx = (st.session_state.key_index + attempt) % num_clients
            client = clients[current_idx]

            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=config,
                )
                
                # Update index key untuk request berikutnya
                st.session_state.key_index = (current_idx + 1) % num_clients
                return response.text

            except Exception as e:
                last_exception = e
                continue

    return f"Maaf, koneksi ke AI sedang padat. Silakan coba bicara lagi. (Detail: {last_exception})"

# ------------------------------------------------------------------------------
# 4. ALUR UTAMA STREAMLIT & AVATAR
# ------------------------------------------------------------------------------
if "last_audio" not in st.session_state:
    st.session_state.last_audio = None

# Tangkap Suara dari Query Parameter
voice_input = st.query_params.get("speech_text", "")

if voice_input:
    # Bersihkan parameter URL
    st.query_params.clear()
    
    with st.spinner("🤖 RoboMANTAP sedang menjawab..."):
        # A. Dapatkan Jawaban AI dengan Rotasi Key
        ai_reply = generate_response_with_rotation(voice_input)

        # B. Ubah Jawaban Teks Menjadi Audio Suara (.mp3)
        text_to_speech(ai_reply, output_file=AUDIO_RESPONSE_PATH)
        
        # C. Simpan Audio ke Session State & Rerun
        st.session_state.last_audio = AUDIO_RESPONSE_PATH
        st.rerun()

# Render Widget Avatar Interaktif
render_interactive_avatar(CHARACTER_IMAGE, audio_path=st.session_state.last_audio)

if voice_input:
    st.success(f"🗣️ **Siswa:** {voice_input}")
