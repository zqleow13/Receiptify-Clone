from flask import Flask, render_template, request, redirect, session
import random
import string
import urllib.parse
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

# Client ID & Redirect URI
CLIENT_ID = os.getenv("client_ID")
REDIRECT_URI = os.getenv("redirect_url")

# Generate random string for state
def generate_random_string(length):
    letters_and_digits = string.ascii_letters + string.digits
    return ''.join(random.choice(letters_and_digits) for i in range(length))

# Login route
@app.route('/login')
def login():
    state = generate_random_string(16)
    scope = 'user-read-private user-read-email' # user-read-private & user-read-email scopes: get current user's profile 
    
    # Redirect user to Spotify authorisation URL
    spotify_auth_url = 'https://accounts.spotify.com/authorize?' + urllib.parse.urlencode({
        'response_type': 'code',
        'client_id': CLIENT_ID,
        'scope': scope,
        'redirect_uri': REDIRECT_URI,
        'state': state,
    })
    return redirect(spotify_auth_url)

if __name__ == 'main':
    app.run(port=9000)
    


