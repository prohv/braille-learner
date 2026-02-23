import asyncio
import json
import threading
from typing import List

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import os

from speech.vosk_recognizer import VoskLetterRecognizer
from speech.intent import parse_intent, IntentType
from braille.mapping import get_braille_pattern
import config

# Initialize FastAPI
app = FastAPI(title="Braille Learner Simulator")

# WebSocket managers
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                pass

manager = ConnectionManager()

# Mount static files - we want them available at root or /static
app.mount("/src", StaticFiles(directory="src"), name="src")

@app.get("/")
async def get():
    with open("src/index.html", "r") as f:
        return HTMLResponse(content=f.read())

@app.get("/style.css")
async def get_css():
    with open("src/style.css", "r") as f:
        return HTMLResponse(content=f.read(), media_type="text/css")

@app.get("/script.js")
async def get_js():
    with open("src/script.js", "r") as f:
        return HTMLResponse(content=f.read(), media_type="application/javascript")

# Serve CSS and JS directly if needed OR just use /static in HTML
# I'll update index.html to use /static/style.css and /static/script.js

class RecognitionWorker:
    def __init__(self, manager: ConnectionManager):
        self.manager = manager
        self.recognizer = None
        self.running = False
        self.loop = None

    def start(self, loop):
        self.loop = loop
        self.running = True
        self.recognizer = VoskLetterRecognizer()
        threading.Thread(target=self._run, daemon=True).start()

    def _run(self):
        print("Recognition worker started")
        while self.running:
            try:
                # This is blocking, but in its own thread
                phrase = self.recognizer.recognize_stream()
                
                if phrase:
                    # Parse intent
                    intent = parse_intent(phrase)
                    
                    # Notify UI about recognition
                    asyncio.run_coroutine_threadsafe(
                        self.manager.broadcast({
                            "type": "recognition",
                            "text": f"Heard: {phrase}"
                        }),
                        self.loop
                    )

                    if intent.type == IntentType.LETTER:
                        letter = intent.value
                        pattern = get_braille_pattern(letter)
                        
                        # Send letter info
                        asyncio.run_coroutine_threadsafe(
                            self.manager.broadcast({
                                "type": "letter",
                                "letter": letter,
                                "pattern": pattern
                            }),
                            self.loop
                        )
                        
                        # Wait for display duration then reset
                        time_to_wait = config.DISPLAY_DURATION
                        threading.Timer(time_to_wait, self._send_reset).start()
                    else:
                        # Immediately ready to hear again if false positive
                        time_to_wait = 1.0  # Just show the wrong text for 1 sec
                        threading.Timer(time_to_wait, self._send_reset).start()

                else:
                    # Timeout or no speech
                    asyncio.run_coroutine_threadsafe(
                        self.manager.broadcast({
                            "type": "status",
                            "value": "LISTENING"
                        }),
                        self.loop
                    )

            except Exception as e:
                print(f"Error in recognition worker: {e}")
                import time
                time.sleep(1)

    def _send_reset(self):
        asyncio.run_coroutine_threadsafe(
            self.manager.broadcast({"type": "reset"}),
            self.loop
        )

worker = RecognitionWorker(manager)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        # Send initial status
        await websocket.send_json({"type": "status", "value": "LISTENING"})
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.on_event("startup")
async def startup_event():
    # Start the recognition worker in the background
    loop = asyncio.get_event_loop()
    worker.start(loop)

if __name__ == "__main__":
    # Ensure src directory exists
    if not os.path.exists("src"):
        os.makedirs("src")
        
    print("Starting server on http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
