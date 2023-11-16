from flask import Flask, render_template, request, session
app = Flask(__name__)

@app.route("/")
def home():
    return "Hello, Flask"