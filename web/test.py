# test.py - Minimal test version
from flask import Flask, render_template, redirect, url_for, session, flash
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'simple-test-key-123'

print("🔧 Testing basic Flask setup...")

@app.route('/')
def home():
    print("🏠 Home page accessed")
    return """
    <h1>✅ Basic Flask Working!</h1>
    <p>If you see this, Flask is working correctly.</p>
    <a href="/test-auth">Test Auth</a>
    """

@app.route('/test-auth')
def test_auth():
    print("🔐 Test auth route")
    return """
    <h1>✅ Auth Test</h1>
    <p>Basic routes are working!</p>
    <a href="/">Home</a>
    """

if __name__ == '__main__':
    print("🚀 Starting SIMPLE test server...")
    app.run(debug=True, port=5001)  # Use different port