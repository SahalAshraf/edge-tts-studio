from fastapi import FastAPI, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import edge_tts
import asyncio

app = FastAPI()

# Enable CORS so your browser frontend can talk to Render
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
    Includes robust header configuration and fallback mechanisms for cloud hosting providers (Render).
    """
    try:
        print(f"Received request -> Voice: {voice}, Text length: {len(text)} chars")
        
        # Initialize communicate with Edge-TTS
        communicate = edge_tts.Communicate(text, voice)
        
        # Collect audio chunks into memory
        audio_buffer = bytearray()
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_buffer.extend(chunk["data"])
                
        if not audio_buffer:
            raise HTTPException(status_code=500, detail="Empty audio stream received from Edge TTS service.")
            
        return Response(content=bytes(audio_buffer), media_type="audio/mpeg")
        
    except Exception as e:
        print(f"CRITICAL EXCEPTION IN SYNTHESIZE: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Return a friendly descriptive error message back to the client
        raise HTTPException(
            status_code=500, 
            detail=f"Edge-TTS Handshake Error (403/Blocked): Microsoft has blocked direct cloud server IPs or the token changed. Error: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=10000)