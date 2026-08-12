from fastapi import FastAPI, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import edge_tts
import traceback
import sys

app = FastAPI()

# Bulletproof CORS configuration for cross-origin browser requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def keep_alive():
    return {"status": "Edge-TTS Server is awake and running!"}

@app.get("/synthesize")
async def synthesize(text: str, voice: str = "hi-IN-SwaraNeural"):
    """
    Generates audio using Microsoft Edge TTS and streams it back as MP3,
    with full exception traceback logging printed to Render console.
    """
    if not text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty.")
    
    try:
        print(f"Received request -> Voice: {voice}, Text length: {len(text)} chars", flush=True)
        
        communicate = edge_tts.Communicate(text, voice)
        audio_buffer = bytearray()
        
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_buffer.extend(chunk["data"])
                
        if len(audio_buffer) == 0:
            print("ERROR: Edge TTS returned empty audio buffer.", flush=True)
            raise HTTPException(status_code=500, detail="No audio data returned from Edge TTS service.")
            
        print(f"Successfully generated {len(audio_buffer)} bytes of audio.", flush=True)
        return Response(content=bytes(audio_buffer), media_type="audio/mpeg")
        
    except Exception as e:
        print("CRITICAL EXCEPTION IN SYNTHESIZE:", flush=True)
        traceback.print_exc(file=sys.stdout)
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=10000)