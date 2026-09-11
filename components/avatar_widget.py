import streamlit.components.v1 as components
import base64
import os

def image_to_base64(image_path: str) -> str:
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode("utf-8")
    return ""

def render_interactive_avatar(image_path: str, audio_path: str = None):
    img_b64 = image_to_base64(image_path)
    img_src = f"data:image/png;base64,{img_b64}" if img_b64 else ""

    audio_trigger_script = ""
    if audio_path and os.path.exists(audio_path):
        audio_trigger_script = f"""
            const audio = new Audio('{audio_path}?t=' + new Date().getTime());
            const avatar = document.getElementById('avatar-img');
            const btn = document.getElementById('mic-btn');
            
            btn.innerText = "🗣️ RoboMANTAP Sedang Menjawab...";
            avatar.classList.add('speaking');
            
            audio.play();
            audio.onended = () => {{
                avatar.classList.remove('speaking');
                btn.innerText = "🎙️ Bicara dengan RoboMANTAP";
            }};
        """

    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                margin: 0;
                background-color: transparent;
                display: flex;
                flex-direction: column;
                align-items: center;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }}
            .avatar-container {{
                width: 280px;
                height: 350px;
                display: flex;
                justify-content: center;
                align-items: center;
                position: relative;
            }}
            
            .avatar-img {{
                max-width: 100%;
                max-height: 100%;
                object-fit: contain;
                animation: breathe 3s ease-in-out infinite;
                transition: transform 0.3s ease, filter 0.3s ease;
                filter: drop-shadow(0 10px 15px rgba(0,0,0,0.3));
            }}

            @keyframes breathe {{
                0% {{ transform: translateY(0px) scale(1); }}
                50% {{ transform: translateY(-10px) scale(1.02); }}
                100% {{ transform: translateY(0px) scale(1); }}
            }}

            .listening {{
                animation: breathe 1.2s ease-in-out infinite;
                filter: drop-shadow(0 0 25px rgba(16, 185, 129, 0.9));
            }}

            .speaking {{
                animation: breathe 0.7s ease-in-out infinite;
                filter: drop-shadow(0 0 25px rgba(59, 130, 246, 0.9));
            }}

            .mic-button {{
                background-color: #047857;
                color: white;
                border: none;
                padding: 14px 28px;
                border-radius: 30px;
                font-size: 16px;
                font-weight: 600;
                cursor: pointer;
                box-shadow: 0 4px 14px rgba(4, 120, 87, 0.4);
                transition: all 0.2s ease;
                margin-top: 15px;
            }}
            .mic-button:hover {{
                background-color: #065f46;
                transform: translateY(-2px) scale(1.03);
            }}
        </style>
    </head>
    <body>

        <div class="avatar-container">
            <img id="avatar-img" class="avatar-img" src="{img_src}" alt="RoboMANTAP Avatar" />
        </div>

        <button class="mic-button" id="mic-btn" onclick="startListening()">
            🎙️ Bicara dengan RoboMANTAP
        </button>

        <script>
            function startListening() {{
                const btn = document.getElementById('mic-btn');
                const avatar = document.getElementById('avatar-img');

                const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
                if (!SpeechRecognition) {{
                    alert("Browser Anda tidak mendukung Speech Recognition. Gunakan Google Chrome atau Microsoft Edge.");
                    return;
                }}

                const recognition = new SpeechRecognition();
                recognition.lang = 'id-ID';

                recognition.onstart = () => {{
                    btn.innerText = "🎧 Mendengarkan... (Silakan Bicara)";
                    avatar.classList.add('listening');
                }};

                recognition.onresult = (event) => {{
                    const transcript = event.results[0][0].transcript;
                    btn.innerText = "⏳ Mengirim data suara...";
                    avatar.classList.remove('listening');

                    // Kirim Teks Suara Langsung ke Streamlit Backend
                    try {{
                        const url = new URL(window.top.location.href);
                        url.searchParams.set("speech_text", transcript);
                        window.top.location.href = url.href;
                    }} catch(e) {{
                        console.error("Gagal mengirim data suara:", e);
                    }}
                }};

                recognition.onerror = (e) => {{
                    avatar.classList.remove('listening');
                    btn.innerText = "🎙️ Bicara dengan RoboMANTAP";
                }};

                recognition.start();
            }}

            {audio_trigger_script}
        </script>
    </body>
    </html>
    """
    return components.html(html_code, height=440)