from urllib.parse import quote_plus, urlencode
from authlib.integrations.flask_client import OAuth
import os
from flask import session, redirect, url_for
from functools import wraps

class Auth0Manager:
    def __init__(self, app):
        self.app = app
        self.oauth = OAuth(app)
        
        auth0_domain = os.getenv('AUTH0_DOMAIN', 'dev-example.us.auth0.com')
        client_id = os.getenv('AUTH0_CLIENT_ID', 'your-client-id')
        client_secret = os.getenv('AUTH0_CLIENT_SECRET', 'your-client-secret')
        
        self.auth0_oauth = self.oauth.register(
            'auth0',
            client_id=client_id,
            client_secret=client_secret,
            client_kwargs={
                'scope': 'openid profile email',
            },
            server_metadata_url=f'https://{auth0_domain}/.well-known/openid-configuration',
            base_url=f'https://{auth0_domain}',
        )
        
        self.auth0_domain = auth0_domain
    
    def login(self):
        """Initiate Auth0 login flow"""
        callback_url = url_for('auth_callback', _external=True)
        return self.auth0_oauth.authorize_redirect(callback_url)
    
    def handle_callback(self):
        """Handle Auth0 callback and return user info"""
        token = self.auth0_oauth.authorize_access_token()
        user_info = token['userinfo']
        return user_info
    
    def logout(self):
        """Logout and clear session"""
        session.clear()
        
        # Construct Auth0 logout URL
        logout_url = (
            f"https://{self.auth0_domain}/v2/logout?"
            + urlencode(
                {
                    "returnTo": url_for('index', _external=True),
                    "client_id": os.getenv('AUTH0_CLIENT_ID', 'your-client-id'),
                },
                quote_via=quote_plus,
            )
        )
        return logout_url

