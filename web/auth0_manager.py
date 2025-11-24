from authlib.integrations.flask_client import OAuth
from flask import url_for
import os
from dotenv import load_dotenv
from urllib.parse import urlencode
from pathlib import Path

# Load .env from root directory (parent of web/)
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

class Auth0Manager:
    def __init__(self, app=None):
        self.oauth = OAuth(app)
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        auth0_domain = os.getenv('AUTH0_DOMAIN')
        client_id = os.getenv('AUTH0_CLIENT_ID')
        client_secret = os.getenv('AUTH0_CLIENT_SECRET')
        
        if not auth0_domain or not client_id or not client_secret:
            raise ValueError(
                "Auth0 configuration missing. Please set AUTH0_DOMAIN, "
                "AUTH0_CLIENT_ID, and AUTH0_CLIENT_SECRET in your .env file"
            )
        
        self.oauth.register(
            name='auth0',
            client_id=client_id,
            client_secret=client_secret,
            client_kwargs={
                'scope': 'openid profile email',
            },
            server_metadata_url=f'https://{auth0_domain}/.well-known/openid-configuration',
            # Disable strict time validation to handle clock skew
            fetch_token=lambda: None,  # Don't fetch token on registration
        )
        
        # Configure the client to be lenient with time validation
        # This helps with clock synchronization issues between local server and Auth0
        if hasattr(self.oauth.auth0, 'client'):
            # Set leeway for token validation (60 seconds)
            self.oauth.auth0.client.leeway = 60
    
    def login(self):
        """Initiate Auth0 login redirect"""
        return self.oauth.auth0.authorize_redirect(
            redirect_uri=url_for('auth_callback', _external=True)
        )
    
    def handle_callback(self):
        """Handle Auth0 callback and retrieve user info"""
        try:
            token = self.oauth.auth0.authorize_access_token()
            
            # Log token structure for debugging
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f"Token keys: {token.keys() if token else 'No token'}")
            
            # Try different ways to get user info
            user_info = token.get('userinfo')
            
            # If userinfo is not in token, try to fetch it from the token endpoint
            if not user_info:
                # Check if user info is in the token itself
                if 'sub' in token or 'email' in token:
                    user_info = {
                        'sub': token.get('sub'),
                        'email': token.get('email'),
                        'name': token.get('name') or token.get('email', '').split('@')[0],
                        'picture': token.get('picture'),
                        'nickname': token.get('nickname'),
                    }
                else:
                    # Fetch user info from Auth0
                    from flask import current_app
                    import requests
                    auth0_domain = os.getenv('AUTH0_DOMAIN')
                    access_token = token.get('access_token')
                    
                    if access_token:
                        response = requests.get(
                            f'https://{auth0_domain}/userinfo',
                            headers={'Authorization': f'Bearer {access_token}'}
                        )
                        if response.status_code == 200:
                            user_info = response.json()
            
            if not user_info:
                raise ValueError("Could not retrieve user information from Auth0")
            
            return user_info
        except Exception as e:
            import logging
            import traceback
            logger = logging.getLogger(__name__)
            logger.error(f"Error in handle_callback: {str(e)}")
            logger.error(traceback.format_exc())
            raise
    
    def logout(self):
        return f"https://{os.getenv('AUTH0_DOMAIN')}/v2/logout?" + urlencode({
            'returnTo': url_for('index', _external=True),
            'client_id': os.getenv('AUTH0_CLIENT_ID'),
        })