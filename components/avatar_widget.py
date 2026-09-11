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
            
            btn.innerText = "🗣️ RoboMANTAP Membalas...";
            avatar.classList.add('speaking');
            
            audio.play().catch(e => console.log("Audio play error:", e));
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

        <button class="mic-button" id="mic-btn" onclick="toggleListening()">
            🎙️ Bicara dengan RoboMANTAP
        </button>

        <script>
            let mediaRecorder = null;
            let audioChunks = [];
            let isRecording = false;
            let autoStopTimer = null;

            async function toggleListening() {{
                const btn = document.getElementById('mic-btn');
                const avatar = document.getElementById('avatar-img');

                if (!isRecording) {{
                    try {{
                        const stream = await navigator.mediaDevices.getUserMedia({{ audio: true }});
                        
                        let mimeType = 'audio/webm';
                        if (!MediaRecorder.isTypeSupported(mimeType)) {{
                            mimeType = 'audio/mp4';
                        }}

                        mediaRecorder = new MediaRecorder(stream, {{ mimeType: mimeType }});
                        audioChunks = [];

                        mediaRecorder.ondataavailable = (event) => {{
                            if (event.data.size > 0) audioChunks.push(event.data);
                        }};

                        mediaRecorder.onstop = () => {{
                            avatar.classList.remove('listening');
                            btn.innerText = "⏳ Memproses jawaban...";

                            const audioBlob = new Blob(audioChunks, {{ type: mimeType }});
                            const reader = new FileReader();
                            reader.readAsDataURL(audioBlob);
                            reader.onloadend = () => {{
                                const base64Audio = reader.result.split(',')[1];
                                try {{
                                    const parentUrl = new URL(window.parent.location.href);
                                    parentUrl.searchParams.set("audio_b64", base64Audio);
                                    window.parent.location.href = parentUrl.href;
                                }} catch (err) {{
                                    window.location.search = "?audio_b64=" + encodeURIComponent(base64Audio);
                                }}
                            }};
                        }};

                        mediaRecorder.start();
                        isRecording = true;
                        btn.innerText = "🔴 Mendengarkan... (Klik Lagi jika Selesai)";
                        avatar.classList.add('listening');

                        // Otomatis stop setelah 7 detik
                        autoStopTimer = setTimeout(() => {{
                            if (isRecording) {{
                                stopRecording();
                            }}
                        }}, 7000);

                    }} catch (err) {{
                        alert("Gagal mengakses mikrofon: " + err.message + "\\nPastikan Anda memberikan izin mikrofon di browser.");
                    }}
                }} else {{
                    stopRecording();
                }}
            }}

            function stopRecording() {{
                if (autoStopTimer) clearTimeout(autoStopTimer);
                if (mediaRecorder && mediaRecorder.state !== "inactive") {{
                    mediaRecorder.stop();
                    mediaRecorder.stream.getTracks().forEach(track => track.stop());
                }}
                isRecording = false;
            }}

            {audio_trigger_script}
        </script>
    </body>
    </html>
    """
    return components.html(html_code, height=440)
