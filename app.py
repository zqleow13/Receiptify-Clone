from flask import Flask, render_template, request, redirect, session, url_for, jsonify
from flask_session import Session
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
import os
import time
from dotenv import load_dotenv
from datetime import datetime, timedelta
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

sp_oauth = SpotifyOAuth(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, scope="user-read-private user-read-email user-top-read")

# Home page
@app.route("/")
def home():
    return render_template("index.html")

# To redirect users to log in to their Spotify accounts and to authorise app
@app.route("/login")
def login():
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

# Once app is authorised, it will redirect users to the ID Card page
@app.route("/callback")
def callback():
    token_info = sp_oauth.get_access_token(request.args["code"])
    session["token_info"] = token_info
    sp = Spotify(auth=token_info["access_token"])
    user_data = sp.me()
    session["user_data"] = user_data
    return redirect(url_for("idcard"))

# ID Card page
@app.route("/idcard")
def idcard():
    if "token_info" not in session:
        return redirect(url_for("login"))
    
    # Get token info from session
    token_info = session["token_info"]
    
    # Check if the access token is expired
    expiration_time = token_info.get("expires_at", 0)
    if expiration_time < time.time():
        # Access token is expired, refresh the token
        token_info = sp_oauth.refresh_access_token(token_info["refresh_token"])
        session["token_info"] = token_info
    
    # Create Spotify object with the access token    
    sp = Spotify(auth=token_info["access_token"])
    
    # To get user data
    user_data = sp.me()
    
    # To show current date for D.O.B of ID card
    now = datetime.now()
    date_time = now.strftime("%d/%m/%Y")
    
    # To show user's last month and last 6 months' top 10 tracks
    last_month_tracks = sp.current_user_top_tracks(10, 0, "short_term")
    last_six_months_tracks = sp.current_user_top_tracks(10, 0, "medium_term")
    
    return render_template(
        "idcard.html", user_data=user_data, date_time=date_time, last_month_tracks=last_month_tracks, last_six_months_tracks=last_six_months_tracks)

# To refresh token after it expires (i.e after 1h)
@app.route("/refresh_token")
def refresh_token():
    if "token_info" not in session:
        return jsonify({'error': "User not logged in"}), 401
    
    # Get token info from session
    token_info = session["token_info"]
    
    # Refresh the access token using the refresh token
    refreshed_token_info = sp_oauth.refresh_access_token(token_info["refresh_token"])
    
    # Update the session with the new token info
    session["token-info"] = refreshed_token_info
    
    return jsonify({"messsage": "Token refreshed successfully"})

# To redirect users back to homepage after logout and to clear their sessions    
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))    

if __name__ == "__main__":
    app.run(debug=True)