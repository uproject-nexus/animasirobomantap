import asyncio
import edge_tts
import os

# Suara Indonesia wanita yang sangat natural & ramah (id-ID-GadisNeural)
VOICE = "id-ID-GadisNeural"

async def generate_speech_async(text: str, output_file: str):
    communicate = edge_tts.Communicate(text, VOICE)
    await communicate.save(output_file)

def text_to_speech(text: str, output_file: str = "temp_response.mp3") -> str:
    """Mengubah teks jawaban AI menjadi file audio mp3."""
    asyncio.run(generate_speech_async(text, output_file))
    return output_file