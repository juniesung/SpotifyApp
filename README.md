# Spotify App

A full-stack web app that connects to your Spotify account, displays your profile, and lays the groundwork for playlist management and listening history features. Built with FastAPI and vanilla JavaScript.

## Features

- **Spotify OAuth 2.0 Login** — redirects users through Spotify's authorization flow and handles the callback to securely exchange tokens
- **Automatic Token Refresh** — silently renews access tokens 2 minutes before expiry without requiring the user to log in again
- **Profile Endpoint** — fetches and returns the authenticated user's Spotify profile data
- **Session Management** — server-side session tracking using secure random session IDs
- **Single Deployable Unit** — frontend is served as static files directly from the FastAPI backend; no separate frontend server needed

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI (Python), Authlib |
| Frontend | Vanilla JavaScript, HTML, CSS |
| Auth | Spotify OAuth 2.0 |
| HTTP Client | httpx (async) |
| Sessions | Starlette SessionMiddleware |

## Project Structure

```
├── server/
│   ├── main.py
│   ├── requirements.txt
│   └── .env.example
├── web/
│   ├── index.html
│   ├── app.js
│   └── styles.css
```

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/auth/login` | Redirects to Spotify authorization page |
| GET | `/auth/callback` | Handles OAuth callback, stores tokens |
| GET | `/api/me` | Returns authenticated user's Spotify profile |

## OAuth Scopes Requested

- `user-read-email` `user-read-private`
- `user-top-read` `user-read-recently-played`
- `playlist-modify-public` `playlist-modify-private`
- `user-library-read`
- `playlist-read-private` `playlist-read-collaborative`

## Getting Started

### Prerequisites
- Python 3.9+
- A Spotify Developer account and registered app

### Setup

```bash
cd server
pip install -r requirements.txt
```

Create a `.env` file (see `.env.example`):
```
SPOTIFY_CLIENT_ID=your_client_id
SPOTIFY_CLIENT_SECRET=your_client_secret
REDIRECT_URI=http://127.0.0.1:8000/auth/callback
SESSION_SECRET=any_random_string
```

In your Spotify Developer Dashboard, add `http://127.0.0.1:8000/auth/callback` as a Redirect URI.

### Run

```bash
uvicorn main:app --reload
```

Visit `http://127.0.0.1:8000` and click login to authenticate with Spotify.
