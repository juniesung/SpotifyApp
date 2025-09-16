import os
from pathlib import Path

import time, secrets
from typing import Optional, Dict, Any
import httpx
from authlib.integrations.starlette_client import OAuth

from fastapi import Request
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SESSION_SECRET", "devkey"))

SPOTIFY_CLIENT_ID = os.environ["SPOTIFY_CLIENT_ID"]
SPOTIFY_CLIENT_SECRET = os.environ["SPOTIFY_CLIENT_SECRET"]
REDIRECT_URI = os.environ.get("REDIRECT_URI", "http://127.0.0.1:8000/auth/callback")

TOKENS: Dict[str, Dict[str, Any]] = {}

oauth = OAuth()
oauth.register(
    name="spotify",
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET,
    authorize_url="https://accounts.spotify.com/authorize",
    access_token_url="https://accounts.spotify.com/api/token",
    client_kwargs={
        # asking for data, add more
        "scope": (
            "user-read-email user-read-private "
            "user-top-read user-read-recently-played "
            "playlist-modify-public playlist-modify-private"
            "user-library-read"
            "playlist-read-private playlist-read-collaborative"
        )
    },
)

def _get_sid(request) -> str:
    sid = request.session.get("sid")
    if not sid:
        sid = secrets.token_urlsafe(16)
        request.session["sid"] = sid
    return sid

async def _get_access_token(request) -> Optional[str]:
    sid = request.session.get("sid")
    if not sid or sid not in TOKENS:
        return None

    token = TOKENS[sid]
    now = int(time.time())
    exp = int(token.get("expires_at", 0))

    # refresh token ~2 min before expiry
    if exp and exp < now + 120 and token.get("refresh_token"):
        async with httpx.AsyncClient(timeout=15) as x:
            r = await x.post(
                "https://accounts.spotify.com/api/token",
                data = {
                    "grant_type": "refresh_token",
                    "refresh_token": token["refresh_token"],
                    "client_id": SPOTIFY_CLIENT_ID,
                    "client_secret": SPOTIFY_CLIENT_SECRET,
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            r.raise_for_status()
            newt = r.json()
            token.update(newt)
            TOKENS[sid] = token
    
    return token.get("access_token")


@app.get("/auth/login")
async def login(request: Request):
    _get_sid(request)
    return await oauth.spotify.authorize_redirect(request, REDIRECT_URI)

@app.get("/auth/callback")
async def callback(request: Request):
    sid = _get_sid(request)
    token = await oauth.spotify.authorize_access_token(request)
    TOKENS[sid] = token
    return RedirectResponse("/")

@app.get("/api/me")
async def me(request: Request):
    # return current user's spotify profile
    access = await _get_access_token(request)
    if not access:
        return JSONResponse({"error": "unauthorized"}, status_code=401)
    
    async with httpx.AsyncClient(timeout=15) as x:
        r = await x.get(
            "https://api.spotify.com/v1/me",
            headers={"Authorization": f"Bearer {access}"},
        )
        return JSONResponse(r.json())
    
    
BASE_DIR = Path(__file__).resolve().parent
WEB_DIR = BASE_DIR.parent / "web"

if WEB_DIR.exists():
    # html=True => serves index.html on "/"
    app.mount("/", StaticFiles(directory=str(WEB_DIR), html=True), name="web")
else:
    @app.get("/")
    def root():
        return {"hint": "Create a web/ folder with index.html to serve a homepage."}