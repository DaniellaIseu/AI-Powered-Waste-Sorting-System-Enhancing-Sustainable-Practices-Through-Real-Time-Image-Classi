import base64
import uuid
from pathlib import Path
import os

from flask import Flask, render_template, redirect, url_for, session, flash, request, jsonify, send_from_directory
from auth0_manager import Auth0Manager
from dotenv import load_dotenv
from functools import wraps
from werkzeug.utils import secure_filename

from classifier import classify_image
from stats_store import get_stats, record_classification

# Load .env from root directory (parent of web/)
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'static', 'uploads')

# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)
app.logger.setLevel(logging.DEBUG)

Path(app.config['UPLOAD_FOLDER']).mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif'}


def _allowed_file(filename: str) -> bool:
    return Path(filename).suffix.lower() in ALLOWED_EXTENSIONS


def _build_metrics(stats):
    categories = stats.get('categories', {})
    total = stats.get('total_items', 0) or 0
    recyclables = sum(categories.get(key, 0) for key in ('plastic', 'glass', 'metal'))
    recycling_rate = round((recyclables / total) * 100, 1) if total else 0
    organic = categories.get('organic', 0)
    other = categories.get('other', 0)
    paper = categories.get('paper', 0)

    eco_impact = {
        'co2_saved_kg': round(recyclables * 0.2, 1),
        'energy_saved_kwh': round(recyclables * 0.5, 1),
        'landfill_space_liters': round(other * 1.5, 1),
    }

    return {
        'total': total,
        'recyclables': recyclables,
        'recycling_rate': recycling_rate,
        'organic': organic,
        'other': other,
        'paper': paper,
        'eco_impact': eco_impact,
    }

# Initialize Auth0
auth0 = Auth0Manager(app)

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

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/login')
def login():
    app.logger.info("Login route called")
    try:
        # Check if we're in a request context
        callback_url = url_for('auth_callback', _external=True)
        app.logger.info(f"Callback URL: {callback_url}")
        
        redirect_response = auth0.login()
        app.logger.info(f"Auth0 login redirect successful: {type(redirect_response)}")
        
        if redirect_response is None:
            raise ValueError("Auth0 login returned None")
            
        return redirect_response
    except Exception as e:
        import traceback
        error_msg = f"Login error: {str(e)}"
        error_trace = traceback.format_exc()
        app.logger.error(error_msg)
        app.logger.error(error_trace)
        flash(f'Login error: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/callback')
def auth_callback():
    app.logger.info("Callback route called")
    try:
        user_info = auth0.handle_callback()
        app.logger.info(f"User info received: {user_info}")
        
        if not user_info:
            raise ValueError("No user info received from Auth0")
        
        session['user'] = user_info
        flash('Successfully logged in!', 'success')
        return redirect(url_for('dashboard'))
    except Exception as e:
        import traceback
        error_msg = f"Authentication failed: {str(e)}"
        error_trace = traceback.format_exc()
        app.logger.error(error_msg)
        app.logger.error(error_trace)
        flash(f'Authentication failed: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(auth0.logout())

@app.route('/dashboard')
@login_required
def dashboard():
    user = session['user']
    stats = get_stats()
    metrics = _build_metrics(stats)
    return render_template(
        'dashboard.html',
        user=user['name'],
        email=user['email'],
        picture=user.get('picture'),
        stats=stats,
        metrics=metrics,
    )

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        file = request.files.get('image')
        if not file or file.filename == '':
            flash('Please choose an image before submitting.', 'error')
            return redirect(url_for('upload'))

        if not _allowed_file(file.filename):
            flash('Unsupported file type. Upload JPG, PNG, or GIF files.', 'error')
            return redirect(url_for('upload'))

        filename = secure_filename(file.filename)
        stem = Path(filename).stem
        ext = Path(filename).suffix
        unique_name = f"{stem}_{uuid.uuid4().hex[:8]}{ext}"
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_name)
        file.save(save_path)

        classification = classify_image(save_path)
        stats = record_classification(
            classification['label'],
            classification['confidence'],
            filename=unique_name,
        )
        metrics = _build_metrics(stats)

        return render_template(
            'upload.html',
            result=classification,
            filename=unique_name,
            stats=stats,
            metrics=metrics,
        )

    stats = get_stats()
    return render_template('upload.html', stats=stats, metrics=_build_metrics(stats))

@app.route('/admin')
@login_required
def admin_dashboard():
    user = session['user']
    stats = get_stats()
    return render_template(
        'admin_dashboard.html',
        user=user['name'],
        email=user['email'],
        picture=user.get('picture'),
        stats=stats,
        metrics=_build_metrics(stats),
    )


@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


# Mobile Authentication API Endpoints (separate from web OAuth flow)
@app.route('/api/login', methods=['POST'])
def api_login():
    """Mobile app login using Auth0 Resource Owner Password Grant"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid request body'}), 400
        
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        # Use Auth0 Resource Owner Password Grant
        import requests
        auth0_domain = os.getenv('AUTH0_DOMAIN')
        client_id = os.getenv('AUTH0_CLIENT_ID')
        client_secret = os.getenv('AUTH0_CLIENT_SECRET')
        
        token_url = f'https://{auth0_domain}/oauth/token'
        
        # Get database connection name for password grant
        # We need to specify the connection in password grant
        import requests as req_lib
        mgmt_token_url = f'https://{auth0_domain}/oauth/token'
        mgmt_payload = {
            'client_id': client_id,
            'client_secret': client_secret,
            'audience': f'https://{auth0_domain}/api/v2/',
            'grant_type': 'client_credentials'
        }
        mgmt_resp = req_lib.post(mgmt_token_url, json=mgmt_payload)
        connection_name = None
        if mgmt_resp.status_code == 200:
            mgmt_token = mgmt_resp.json().get('access_token')
            conn_resp = req_lib.get(
                f'https://{auth0_domain}/api/v2/connections',
                headers={'Authorization': f'Bearer {mgmt_token}'},
                params={'strategy': 'auth0'}
            )
            if conn_resp.status_code == 200:
                connections = conn_resp.json()
                for conn in connections:
                    if conn.get('strategy') == 'auth0' and client_id in conn.get('enabled_clients', []):
                        connection_name = conn.get('name')
                        break
                    if not connection_name and conn.get('strategy') == 'auth0':
                        connection_name = conn.get('name')
        
        payload = {
            'grant_type': 'password',
            'username': email,
            'password': password,
            'client_id': client_id,
            'client_secret': client_secret,
            'scope': 'openid profile email'
        }
        
        # Add connection if found (required for some Auth0 configurations)
        if connection_name:
            payload['connection'] = connection_name
        
        response = requests.post(token_url, json=payload)
        
        if response.status_code != 200:
            error_msg = response.json().get('error_description', 'Invalid email or password')
            return jsonify({'error': error_msg}), 401
        
        token_data = response.json()
        access_token = token_data.get('access_token')
        id_token = token_data.get('id_token')
        
        # Get user info from Auth0
        userinfo_url = f'https://{auth0_domain}/userinfo'
        user_response = requests.get(
            userinfo_url,
            headers={'Authorization': f'Bearer {access_token}'}
        )
        
        if user_response.status_code != 200:
            return jsonify({'error': 'Failed to retrieve user information'}), 500
        
        user_info = user_response.json()
        
        return jsonify({
            'access_token': access_token,
            'id_token': id_token,
            'user': {
                'sub': user_info.get('sub'),
                'name': user_info.get('name'),
                'email': user_info.get('email'),
                'picture': user_info.get('picture')
            }
        }), 200
        
    except Exception as e:
        app.logger.error(f"API login error: {str(e)}", exc_info=True)
        return jsonify({'error': f'Login failed: {str(e)}'}), 500


@app.route('/api/register', methods=['POST'])
def api_register():
    """Mobile app registration using Auth0 Management API"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid request body'}), 400
        
        email = data.get('email')
        password = data.get('password')
        name = data.get('name')
        
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        # Validate password strength
        if len(password) < 8:
            return jsonify({'error': 'Password must be at least 8 characters'}), 400
        
        import requests
        auth0_domain = os.getenv('AUTH0_DOMAIN')
        client_id = os.getenv('AUTH0_CLIENT_ID')
        client_secret = os.getenv('AUTH0_CLIENT_SECRET')
        
        # Get Management API token
        mgmt_token_url = f'https://{auth0_domain}/oauth/token'
        mgmt_payload = {
            'client_id': client_id,
            'client_secret': client_secret,
            'audience': f'https://{auth0_domain}/api/v2/',
            'grant_type': 'client_credentials'
        }
        
        mgmt_response = requests.post(mgmt_token_url, json=mgmt_payload)
        
        if mgmt_response.status_code != 200:
            return jsonify({'error': 'Failed to authenticate with Auth0 Management API'}), 500
        
        mgmt_token = mgmt_response.json().get('access_token')
        
        # Get available database connections
        connections_url = f'https://{auth0_domain}/api/v2/connections'
        connections_response = requests.get(
            connections_url,
            headers={'Authorization': f'Bearer {mgmt_token}'},
            params={'strategy': 'auth0'}  # Only get database connections
        )
        
        # Find the database connection to use
        database_connection = None
        if connections_response.status_code == 200:
            connections = connections_response.json()
            # Try to find 'Username-Password-Authentication' or any enabled database connection
            for conn in connections:
                if conn.get('strategy') == 'auth0' and conn.get('enabled_clients'):
                    # Check if our client is enabled for this connection
                    if client_id in conn.get('enabled_clients', []):
                        database_connection = conn.get('name')
                        break
                # Fallback: use first enabled database connection
                if conn.get('strategy') == 'auth0' and not database_connection:
                    database_connection = conn.get('name')
        
        # If no connection found, try default name or common alternatives
        if not database_connection:
            # Try common names
            for default_name in ['Username-Password-Authentication', 'email', 'db', 'database']:
                # Quick check if connection exists
                test_conn = requests.get(
                    f'https://{auth0_domain}/api/v2/connections?name={default_name}',
                    headers={'Authorization': f'Bearer {mgmt_token}'}
                )
                if test_conn.status_code == 200 and test_conn.json():
                    database_connection = default_name
                    break
        
        if not database_connection:
            app.logger.error("No database connection found in Auth0")
            return jsonify({
                'error': 'No database connection configured in Auth0. Please create a database connection in Auth0 Dashboard.'
            }), 500
        
        # Create user via Management API
        create_user_url = f'https://{auth0_domain}/api/v2/users'
        create_user_payload = {
            'email': email,
            'password': password,
            'connection': database_connection,
            'email_verified': False,
            'verify_email': False  # Set to True if you want Auth0 to send verification email
        }
        
        if name:
            create_user_payload['name'] = name
            create_user_payload['nickname'] = name.split()[0] if name else None
        
        create_response = requests.post(
            create_user_url,
            json=create_user_payload,
            headers={'Authorization': f'Bearer {mgmt_token}'}
        )
        
        if create_response.status_code not in [200, 201]:
            error_data = create_response.json()
            error_msg = error_data.get('message', 'Failed to create user')
            if 'already exists' in error_msg.lower():
                error_msg = 'Email already registered'
            return jsonify({'error': error_msg}), 400
        
        user_data = create_response.json()
        user_sub = user_data.get('user_id')
        
        # Now login the user using Resource Owner Password Grant
        token_url = f'https://{auth0_domain}/oauth/token'
        token_payload = {
            'grant_type': 'password',
            'username': email,
            'password': password,
            'client_id': client_id,
            'client_secret': client_secret,
            'scope': 'openid profile email'
        }
        
        token_response = requests.post(token_url, json=token_payload)
        
        if token_response.status_code != 200:
            # User created but login failed - return user info anyway
            return jsonify({
                'access_token': None,
                'id_token': None,
                'user': {
                    'sub': user_sub,
                    'name': user_data.get('name') or name,
                    'email': email,
                    'picture': user_data.get('picture')
                },
                'message': 'User created successfully. Please login.'
            }), 201
        
        token_data = token_response.json()
        access_token = token_data.get('access_token')
        id_token = token_data.get('id_token')
        
        # Get user info
        userinfo_url = f'https://{auth0_domain}/userinfo'
        user_response = requests.get(
            userinfo_url,
            headers={'Authorization': f'Bearer {access_token}'}
        )
        
        user_info = user_response.json() if user_response.status_code == 200 else {
            'sub': user_sub,
            'email': email,
            'name': name or email.split('@')[0]
        }
        
        return jsonify({
            'access_token': access_token,
            'id_token': id_token,
            'user': {
                'sub': user_info.get('sub', user_sub),
                'name': user_info.get('name') or name,
                'email': user_info.get('email', email),
                'picture': user_info.get('picture')
            }
        }), 201
        
    except Exception as e:
        app.logger.error(f"API register error: {str(e)}", exc_info=True)
        return jsonify({'error': f'Registration failed: {str(e)}'}), 500


@app.route('/api/stats', methods=['GET'])
def api_stats():
    stats = get_stats()
    return jsonify({**stats, 'metrics': _build_metrics(stats)})


def _save_base64_image(image_base64: str) -> str:
    header, _, encoded = image_base64.partition(',')
    data = base64.b64decode(encoded or header)
    filename = f"capture_{uuid.uuid4().hex}.jpg"
    save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    with open(save_path, 'wb') as fh:
        fh.write(data)
    return filename, save_path


@app.route('/api/classify', methods=['POST'])
def api_classify():
    if 'image' in request.files:
        file = request.files['image']
        if not file or file.filename == '':
            return jsonify({'error': 'Missing image file.'}), 400
        if not _allowed_file(file.filename):
            return jsonify({'error': 'Unsupported file type.'}), 400
        filename = secure_filename(file.filename)
        stem = Path(filename).stem
        ext = Path(filename).suffix
        filename = f"{stem}_{uuid.uuid4().hex[:8]}{ext}"
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(save_path)
    else:
        payload = request.get_json(silent=True) or {}
        image_base64 = payload.get('image_base64')
        if not image_base64:
            return jsonify({'error': 'No image provided.'}), 400
        filename, save_path = _save_base64_image(image_base64)

    classification = classify_image(save_path)
    stats = record_classification(
        classification['label'],
        classification['confidence'],
        filename=filename,
    )

    return jsonify({
        'classification': classification,
        'filename': filename,
        'stats': stats,
        'file_url': url_for('uploaded_file', filename=filename, _external=True),
    })


if __name__ == '__main__':
    # Bind to 0.0.0.0 to allow Android emulator to connect via 10.0.2.2
    app.run(host='0.0.0.0', port=5000, debug=True)