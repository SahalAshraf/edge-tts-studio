from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
import edge_tts
import asyncio

app = FastAPI()

# Enable CORS so your browser frontend hosted anywhere can talk to Render
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def keep_alive():
    return {"status": "Edge-TTS Server is awake and running!"}

@app.get("/synthesize")
async def synthesize(text: str, voice: str = "en-US-AriaNeural"):
    """
    Generates audio using Microsoft Edge TTS and streams it back as MP3.
    Popular Voices: 
      - Hindi (In): 'hi-IN-SwaraNeural' (Female), 'hi-IN-MadhurNeural' (Male)
      - US English: 'en-US-AriaNeural' (Female), 'en-US-GuyNeural' (Male)
      - British English: 'en-GB-SoniaNeural' (Female), 'en-GB-RyanNeural' (Male)
    """
    communicate = edge_tts.Communicate(text, voice)
    
    # Collect audio chunks into memory buffer
    audio_buffer = bytearray()
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_buffer.extend(chunk["data"])
            
    return Response(content=bytes(audio_buffer), media_type="audio/mpeg")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=10000)