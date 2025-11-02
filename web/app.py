from flask import Flask, render_template, redirect, url_for, session, flash, request, jsonify
from werkzeug.utils import secure_filename
from functools import wraps 
import os
import sqlite3
from datetime import datetime
import numpy as np
try:
    from tensorflow.keras.models import load_model  # type: ignore
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False
    print("TensorFlow not available, using mock classifications")
from PIL import Image
import io
from auth0_manager import Auth0Manager

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB max file size
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize Auth0
auth0 = Auth0Manager(app)

# Load waste classification model
CLASSES = ['cardboard', 'glass', 'metal', 'paper', 'plastic', 'trash']
model_path = os.path.join('..', 'waste_classifier.h5')
model = None  # Initialize model variable

if TF_AVAILABLE:
    try:
        if os.path.exists(model_path):
            model = load_model(model_path)
            print(f"Model loaded successfully from {model_path}")
        else:
            print(f"Model file not found at {model_path}")
            model = None
    except Exception as e:
        print(f"Error loading model: {e}")
        model = None
else:
    print("TensorFlow not available, using mock classifications")
    model = None

# Initialize database
def init_db():
    conn = sqlite3.connect('waste_sorter.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            auth0_id TEXT UNIQUE NOT NULL,
            username TEXT NOT NULL,
            email TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS classifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            image_path TEXT NOT NULL,
            waste_type TEXT NOT NULL,
            confidence REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    conn.commit()
    conn.close()

init_db()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/login')
def login():
    return auth0.login()

@app.route('/callback')
def auth_callback():
    try:
        user_info = auth0.handle_callback()
        session['user'] = user_info
        
        # Save user to database
        conn = sqlite3.connect('waste_sorter.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR IGNORE INTO users (auth0_id, username, email)
            VALUES (?, ?, ?)
        ''', (user_info.get('sub'), user_info.get('name'), user_info.get('email')))
        conn.commit()
        
        # Get user ID
        cursor.execute('SELECT id FROM users WHERE auth0_id = ?', (user_info.get('sub'),))
        user_row = cursor.fetchone()
        if user_row:
            session['user_id'] = user_row[0]
        
        conn.close()
        
        flash('Successfully logged in!', 'success')
        return redirect(url_for('dashboard'))
    except Exception as e:
        print(f"Auth callback error: {e}")
        flash('Authentication failed. Please try again.', 'error')
        return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(auth0.logout())

@app.route('/dashboard')
@login_required
def dashboard():
    user = session.get('user', {})
    return render_template('dashboard.html', user=user.get('name', 'User'), picture=user.get('picture'))

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        if 'image' not in request.files:
            flash('No image file provided', 'error')
            return redirect(request.url)
        
        file = request.files['image']
        if file.filename == '':
            flash('No image selected', 'error')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{timestamp}_{filename}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Classify image
            result = classify_waste(filepath)
            
            if result:
                # Save classification to database
                conn = sqlite3.connect('waste_sorter.db')
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO classifications (user_id, image_path, waste_type, confidence)
                    VALUES (?, ?, ?, ?)
                ''', (session.get('user_id'), filepath, result['class'], result['confidence']))
                conn.commit()
                conn.close()
                
                return render_template('upload.html', 
                                     result=result,
                                     image_path=filepath,
                                     user=session.get('user', {}).get('name', 'User'))
            else:
                flash('Classification failed', 'error')
                return redirect(url_for('dashboard'))
        
        flash('Invalid file type', 'error')
        return redirect(request.url)
    
    return render_template('upload.html', user=session.get('user', {}).get('name', 'User'))

@app.route('/stats')
@login_required
def stats():
    user_id = session.get('user_id')
    if not user_id:
        flash('User not found', 'error')
        return redirect(url_for('dashboard'))
    
    conn = sqlite3.connect('waste_sorter.db')
    cursor = conn.cursor()
    
    # Get total statistics
    cursor.execute('''
        SELECT waste_type, COUNT(*) as count
        FROM classifications
        WHERE user_id = ?
        GROUP BY waste_type
    ''', (user_id,))
    
    results = cursor.fetchall()
    stats_dict = {row[0]: row[1] for row in results}
    
    # Calculate statistics
    total_items = sum(stats_dict.values())
    recyclables = stats_dict.get('cardboard', 0) + stats_dict.get('glass', 0) + \
                  stats_dict.get('metal', 0) + stats_dict.get('paper', 0) + \
                  stats_dict.get('plastic', 0)
    recycling_rate = (recyclables / total_items * 100) if total_items > 0 else 0
    
    stats = {
        'items_classified': total_items,
        'recycling_rate': round(recycling_rate, 1),
        'plastics': stats_dict.get('plastic', 0),
        'organics': stats_dict.get('trash', 0),
        'paper': stats_dict.get('paper', 0),
        'glass': stats_dict.get('glass', 0),
        'metals': stats_dict.get('metal', 0),
        'cardboard': stats_dict.get('cardboard', 0)
    }
    
    conn.close()
    
    return render_template('stats.html', stats=stats, user=session.get('user', {}).get('name', 'User'))

@app.route('/eco_stats')
@login_required
def eco_stats():
    user_id = session.get('user_id')
    if not user_id:
        flash('User not found', 'error')
        return redirect(url_for('dashboard'))
    
    # Calculate environmental impact based on waste classifications
    conn = sqlite3.connect('waste_sorter.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT waste_type, COUNT(*) as count
        FROM classifications
        WHERE user_id = ?
        GROUP BY waste_type
    ''', (user_id,))
    
    results = cursor.fetchall()
    stats_dict = {row[0]: row[1] for row in results}
    conn.close()
    
    # Environmental impact multipliers (kg CO2 saved per item recycled)
    impact_multipliers = {
        'cardboard': 0.8,
        'glass': 0.3,
        'metal': 2.5,
        'paper': 1.5,
        'plastic': 0.5,
        'trash': 0.0
    }
    
    total_co2_saved = sum(stats_dict.get(key, 0) * impact_multipliers.get(key, 0) for key in impact_multipliers)
    total_items = sum(stats_dict.values())
    
    eco_stats = {
        'co2_saved_kg': round(total_co2_saved, 2),
        'landfill_diverted_kg': round(total_items * 0.3, 2),
        'water_saved_l': round(total_co2_saved * 50, 2),
        'energy_saved_kwh': round(total_co2_saved * 2.5, 2)
    }
    
    return render_template('eco_stats.html', eco=eco_stats, user=session.get('user', {}).get('name', 'User'))

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def classify_waste(image_path):
    """Classify waste using the loaded model"""
    if model is None:
        # Return a mock classification for testing
        import random
        mock_classes = ['cardboard', 'glass', 'metal', 'paper', 'plastic', 'trash']
        return {
            'class': random.choice(mock_classes),
            'confidence': round(random.uniform(70.0, 95.0), 2)
        }
    
    try:
        # Load and preprocess image
        img = Image.open(image_path)
        img = img.resize((224, 224))
        
        # Convert image to RGB if necessary
        if img.mode != 'RGB':
            img = img.convert('RGB')
            
        img_array = np.array(img) / 255.0
        img_array = np.expand_dims(img_array, axis=0)
        
        # Predict
        predictions = model.predict(img_array)
        predicted_class_idx = np.argmax(predictions[0])
        confidence = float(predictions[0][predicted_class_idx] * 100)
        predicted_class = CLASSES[predicted_class_idx]
        
        return {
            'class': predicted_class,
            'confidence': round(confidence, 2)
        }
    except Exception as e:
        print(f"Error classifying image: {e}")
        return None

if __name__ == '__main__':
    app.run(debug=True, port=5000)