from flask import Flask, render_template, request, redirect, session, jsonify, url_for
from flask_session import Session
import base64
import requests
import random
import string
import urllib.parse
import json
from spotipy import Spotify
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

sp_oauth = SpotifyOAuth(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, scope="user-read-private user-read-email")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/login")
def login():
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route("/callback")
def callback():
    token_info = sp_oauth.get_access_token(request.args["code"])
    session["token_info"] = token_info
    sp = Spotify(auth=token_info["access_token"])
    user_data = sp.me()
    session["user_data"] = user_data
    return redirect(url_for("profile"))

@app.route("/idcard")
def profile():
    if "token_info" not in session:
        return redirect(url_for("login"))
    
    token_info = session["token_info"]
    sp = Spotify(auth=token_info["access_token"])
    user_data = sp.me()
    return render_template("idcard.html", user_data=user_data)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)