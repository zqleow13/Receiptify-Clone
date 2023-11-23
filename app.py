from flask import Flask, render_template, request, redirect, session, jsonify, url_for
from flask_session import Session
import base64
import requests
import random
import string
import urllib.parse
import json
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

# Configure session
app.config["SESSION_TYPE"] = 'filesystem'
Session(app)

# Client ID & Redirect URI
CLIENT_ID = os.getenv("client_ID")
CLIENT_SECRET = os.getenv("client_SECRET")
REDIRECT_URI = os.getenv("redirect_uri")

# Secret key
# print(os.urandom(12))
app.secret_key = os.getenv('secret_key')

# Generate random string for state
def generate_random_string(length):
    letters_and_digits = string.ascii_letters + string.digits
    return ''.join(random.choice(letters_and_digits) for i in range(length))


# root state
@app.route('/')
def home():
    return render_template("index.html")


# Login route
@app.route('/login')
def login():
    session.clear()
    state = generate_random_string(16)
    scope = 'user-read-private user-read-email' # user-read-private & user-read-email scopes: get current user's profile 
    
    session['state'] = state
    
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
    new_state = request.args.get('state', None)
    
    print(f"Code: {code}")
    print(f"New State: {new_state}")
    
    # Retrieve the stored state from the session
    stored_state = session.get('state', None)

    if new_state != stored_state:
        return redirect(url_for('error', error_message='state_mismatch'))
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
        
        if 'access_token' in token_info:
            # Save token info to session
            session['access_token'] = token_info['access_token']
            session['refresh_token'] = token_info.get('refresh_token', None)
            
            # Use the access token to get user's profile information
            user_profile_url = 'https://api.spotify.com/v1/me'
            HEADERS = {'Authorization': 'Bearer ' + session['access_token']}
            user_response = requests.get(user_profile_url, headers=HEADERS)
            USER_DATA = user_response.json()
            
            # Store user data in the session
            session['user_data'] = USER_DATA
            
            # Redirect the user to the id card page aka idcard.html
            return render_template('idcard.html', user_data=USER_DATA)
        
        else:
            # To return error message if access token is not present
            return redirect(url_for('error', error_message='token_error'))
        

        

@app.route('/idcard')
def idcard():
    # Check if 'user_data' is present in the session
    if 'user_data' in session:
        # Retrieve 'user_data' from the session
        USER_DATA = session['user_data']
        return render_template('idcard.html', user_data=USER_DATA)
    else:
        # Handle the case where 'user_data' is not present
        return redirect(url_for('error', error_message='user_data_not_found'))

        
        
# Error route
@app.route('/error')
def error():
    error_message = request.args.get('error_message', 'An error occurred')
    return f'Error: {error_message}'

    
# Refresh access token
@app.route('/refresh_token', methods=['GET'])
def refresh_token():
    refresh_token = request.args.get('refresh_token')

    auth_options = {
        'url': 'https://accounts.spotify.com/api/token',
        'headers': {
            'content-type': 'application/x-www-form-urlencoded',
            'Authorization': 'Basic ' + base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
        },
        'data': {
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token
        }
    }

    response = requests.post(auth_options['url'], data=auth_options['data'], headers=auth_options['headers'])

    if response.status_code == 200:
        data = response.json()
        access_token = data.get('access_token')
        new_refresh_token = data.get('refresh_token', refresh_token)

        return jsonify({
            'access_token': access_token,
            'refresh_token': new_refresh_token
        })
    else:
        return jsonify({'error': 'Unable to refresh token'}), response.status_code


if __name__ == '__main__':
    app.run(debug=True)