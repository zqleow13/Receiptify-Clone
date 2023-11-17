from flask import Flask, render_template, request, redirect, session
import base64
import requests
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
CLIENT_SECRET = os.getenv("client_SECRET")
REDIRECT_URI = os.getenv("redirect_uri")

# Generate random string for state
def generate_random_string(length):
    letters_and_digits = string.ascii_letters + string.digits
    return ''.join(random.choice(letters_and_digits) for i in range(length))

# root state
@app.route('/')
def home():
    return 'Hello, World!'

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

# Request access token from Spotify
@app.route('/callback')
def callback():
    code = request.args.get('code', None)
    state = request.args.get('state', None)

    if state is None:
        return redirect('/#' + urllib.parse.urlencode({'error': 'state_mismatch'}))
    else:
        auth_options = {
            'url': 'https://accounts.spotify.com/api/token',
            'data': {
                'code': code,
                'redirect_uri': REDIRECT_URI,
                'grant_type': 'authorization_code'
            },
            'headers': {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Authorization': 'Basic ' + base64.b64encode(f'{CLIENT_ID}:{CLIENT_SECRET}'.encode()).decode()
            }
        }

        response = requests.post(auth_options['url'], data=auth_options['data'], headers=auth_options['headers'])
        token_info = response.json()

        # Handle the token information as needed (e.g., save it to session, database, etc.)
        # For demonstration purposes, printing the token information
        print(token_info)

        return 'Token obtained successfully'
    
    # Refresh access token

if __name__ == 'main':
    app.run()